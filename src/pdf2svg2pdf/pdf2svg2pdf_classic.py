#!/usr/bin/env python3
import concurrent.futures
import re
import subprocess
import tempfile
from collections import Counter
from functools import partial
from pathlib import Path

import fire
import fitz


def create_folders(inpath: Path, outdir: Path):
    inpath_stem = inpath.stem
    folders = [
        outdir / f"{inpath_stem}-pdf-t",
        outdir / f"{inpath_stem}-svg-q",
        outdir / f"{inpath_stem}-pdf-q",
    ]
    for folder in folders:
        folder.mkdir(parents=True, exist_ok=True)
    return folders


def separate_pdf_with_filters(inpath: Path, stem, outdir: Path) -> list[Path]:
    doc = fitz.open(inpath)
    output_dir = outdir / f"{stem}-pdf-t"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_files = []
    for i in range(len(doc)):
        doc.load_page(i)
        output_file = output_dir / f"{stem}-{i:04d}.pdf"
        single_page_doc = fitz.open()
        single_page_doc.insert_pdf(doc, from_page=i, to_page=i)
        single_page_doc.save(output_file)
        single_page_doc.close()
        output_files.append(output_file)
    return output_files


def separate_pdf_no_filters(inpath: Path, stem, outdir: Path) -> list[Path]:
    output = outdir / f"{stem}-pdf-t" / f"{stem}-%04d.pdf"
    cmd = f"pdfseparate {inpath} {output}"
    subprocess.run(cmd, shell=True, check=True)
    return list(output.parent.glob("*.pdf"))


def separate_pdf(inpath: Path, outdir: Path, pdf_filters=()) -> list[Path]:
    stem = inpath.stem
    if not pdf_filters:
        return separate_pdf_no_filters(inpath, stem, outdir)
    if isinstance(pdf_filters, str):
        pdf_filters = [eval(pdf_filter) for pdf_filter in pdf_filters.split(",")]
    with open(inpath, "rb") as f:
        pdf_bytes = f.read()
    for pdf_filter in pdf_filters:
        pdf_bytes = pdf_filter(pdf_bytes)
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(pdf_bytes)
        tmp_path = Path(tmp.name)
    inpath = tmp_path
    return separate_pdf_with_filters(inpath, stem, outdir)


def convert_pdf_to_svg(pdf: Path, outdir: Path) -> Path:
    output = outdir / f"{pdf.stem}.svg"
    cmd = f"pdftocairo -svg {pdf} {output}"
    subprocess.run(cmd, shell=True, check=True)
    return output


def convert_svg_to_pdf(svg: Path, outdir: Path) -> Path:
    output = outdir / f"{svg.stem}.pdf"
    cmd = f"cairosvg -f pdf -o {output} {svg}"
    subprocess.run(cmd, shell=True, check=True)
    return output


def unite_pdfs(pdf_files: list[Path], inpath: Path, outdir: Path):
    inpath_stem = inpath.stem
    output = outdir / f"{inpath_stem}-q.pdf"
    source_files = " ".join(str(pdf) for pdf in pdf_files)
    cmd = f"pdfunite {source_files} {output}"
    subprocess.run(cmd, shell=True, check=True)


def chain_convert(args, pdf_filters=(), svg_filters=()):
    pdf, svg_q_folder, pdf_q_folder = args
    svg = convert_pdf_to_svg(pdf, svg_q_folder)

    if svg_filters:
        if isinstance(svg_filters, str):
            old_filters = svg_filters.split(",")
            svg_filters = []
            for svg_filter in old_filters:
                svg_filter = (
                    eval(f"lambda svg: svg{svg_filter}")
                    if svg_filter.startswith(".")
                    else eval(svg_filter)
                )
                svg_filters.append(svg_filter)
        with open(svg) as svg_file:
            svg_content = svg_file.read()

        for svg_filter in svg_filters:
            svg_content = svg_filter(svg_content)

        with open(svg, "w") as svg_file:
            svg_file.write(svg_content)

    return convert_svg_to_pdf(svg, pdf_q_folder)


def process_single_pdf(inpath: Path, outdir: Path, pdf_filters=None, svg_filters=None):
    pdf_t_folder, svg_q_folder, pdf_q_folder = create_folders(inpath, outdir)

    pdf_list = separate_pdf(inpath, outdir, pdf_filters)

    with concurrent.futures.ProcessPoolExecutor() as executor:
        tasks = [(pdf, svg_q_folder, pdf_q_folder) for pdf in pdf_list]
        chain_convert_func = partial(
            chain_convert, pdf_filters=pdf_filters, svg_filters=svg_filters
        )
        converted_pdfs = list(executor.map(chain_convert_func, tasks))

    unite_pdfs(sorted(converted_pdfs), inpath, outdir)

    print(f"{outdir / f'{inpath.stem}-q.pdf'}")


def process_task_with_filters(args):
    task, pdf_filters, svg_filters = args
    inpath, outdir = task
    return process_single_pdf(
        inpath, outdir, pdf_filters=pdf_filters, svg_filters=svg_filters
    )


def process_task_no_filters(task):
    return process_single_pdf(*task)


def chain_convert_with_filters(args, pdf_filters, svg_filters):
    return chain_convert(args, pdf_filters=pdf_filters, svg_filters=svg_filters)


def pdf2svg2pdf(
    inpath: str, outdir: str = None, dir: bool = False, pdf_filters=(), svg_filters=()
):
    if outdir is None:
        outdir = Path(inpath).parent
    else:
        outdir = Path(outdir)
        outdir.mkdir(parents=True, exist_ok=True)

    if dir:
        infolder = Path(inpath)
        pdf_files = list(infolder.glob("*.pdf"))
    else:
        pdf_files = [Path(inpath)]

    with concurrent.futures.ProcessPoolExecutor() as executor:
        tasks = [(pdf, outdir / pdf.stem) for pdf in pdf_files]
        if svg_filters or pdf_filters:
            process_func = process_task_with_filters
            tasks_with_filters = [(task, pdf_filters, svg_filters) for task in tasks]
            list(executor.map(process_func, tasks_with_filters))
        else:
            process_func = process_task_no_filters
            list(executor.map(process_func, tasks))


def svgo(svg):
    return subprocess.run(
        "svgo --input - --output -",
        shell=True,
        text=True,
        input=svg,
        capture_output=True,
        check=True,
    ).stdout


def pdf_grayscale(pdf_bytes):
    cmd = (
        "gs -sOutputFile=- -sDEVICE=pdfwrite -sColorConversionStrategy=Gray "
        "-dProcessColorModel=/DeviceGray -dCompatibilityLevel=1.4 -dNOPAUSE -dBATCH -_"
    )
    proc = subprocess.run(
        cmd,
        shell=True,
        input=pdf_bytes,
        capture_output=True,
        check=True,
    )
    return proc.stdout


def svg_frequency_fills(svg):
    return sorted(Counter(re.findall(r"fill:(.*?);", svg)).items(), key=lambda x: -x[1])


def svg_transparent_white(svg):
    return re.sub(r"fill:rgb\(100%,100%,100%\);", r"fill:none;", svg)


def svg_one_fill(svg, freq_index):
    svg = svg_transparent_white(svg)
    svg_fill_freq = svg_frequency_fills(svg)

    if len(svg_fill_freq) > 1:
        frequent_fill = svg_fill_freq[freq_index][0]
        svg = re.sub(r"fill:(?!none;)(.*?);", f"fill:{frequent_fill};", svg)
    return svg


def svg_fill0(svg):
    return svg_one_fill(svg, 0)


def svg_fill1(svg):
    return svg_one_fill(svg, 1)


def cli():
    fire.Fire(pdf2svg2pdf)


if __name__ == "__main__":
    cli()
