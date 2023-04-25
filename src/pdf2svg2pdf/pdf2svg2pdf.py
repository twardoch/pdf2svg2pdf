#!/usr/bin/env python3
import logging
import re
import subprocess
from pathlib import Path
from typing import List

import fitz
import fire

logger = logging.getLogger(__name__)


class PDF2SVG2PDF:
    def __init__(
        self,
        inpath: str,
        outdir: str = None,
        advanced: bool = False,
        backends: List[str] = [],
        verbose: bool = False,
        pdf_filters=[],
        svg_filters=[],
    ):
        self.inpath = Path(inpath)
        self.stem = self.inpath.stem
        self.outdir = self.inpath.parent if outdir is None else Path(outdir)
        self.pdf_t_dir = self.outdir / f"{self.stem}-pdf-t"
        self.pdf_q_dir = self.outdir / f"{self.stem}-pdf-q"
        self.svg_q_dir = self.outdir / f"{self.stem}-svg-q"
        for dirname in (self.outdir, self.pdf_t_dir, self.pdf_q_dir, self.svg_q_dir):
            if not dirname.exists():
                dirname.mkdir(parents=True, exist_ok=True)
        self.pdf_q_path = self.outdir / f"{self.stem}-q.pdf"
        if advanced:
            self.backends = ["poppler", "pdfcairo", "cairosvg"]
        elif backends:
            self.backends = backends
        else:
            self.backends = ["poppler", "pdfcairo", "cairosvg"]

        self.verbose = verbose
        if self.verbose:
            logging.basicConfig(level=logging.INFO)
        else:
            logging.basicConfig(level=logging.WARNING)

    def convert_pdf_to_pdfpages_fitz(self, pdf_path: Path, outdir: Path) -> List[Path]:
        logger.info(f"Converting {pdf_path} to PDF pages using Fitz")
        doc = fitz.open(pdf_path)
        output_paths = []
        for i in range(len(doc)):
            page = doc.load_page(i)
            output_path = outdir / f"{pdf_path.stem}-{i:04d}.pdf"
            single_page_doc = fitz.open()
            single_page_doc.insert_pdf(doc, from_page=i, to_page=i)
            single_page_doc.save(output_path)
            single_page_doc.close()
            output_paths.append(output_path)
        return output_paths

    def convert_pdf_to_pdfpages_poppler(
        self, pdf_path: Path, outdir: Path
    ) -> List[Path]:
        logger.info(f"Converting {pdf_path} to PDF pages using Poppler")
        output_pathmask = outdir / f"{pdf_path.stem}-%04d.pdf"
        cmd = f"pdfseparate {pdf_path} {output_pathmask}"
        subprocess.run(cmd, shell=True, check=True)
        return list(outdir.glob("*.pdf"))

    def convert_pdf_to_pdfpages(self, pdf_path: Path, outdir: Path) -> list[Path]:
        if "fitz" in self.backends:
            fn = self.convert_pdf_to_pdfpages_fitz
        elif "poppler" in self.backends:
            fn = self.convert_pdf_to_pdfpages_poppler
        else:
            fn = self.convert_pdf_to_pdfpages_fitz
        return fn(pdf_path, outdir)

    def convert_pdf_to_svg_pdftocairo(self, pdf_path: Path, svg_path: Path) -> Path:
        logger.info(f"Converting {pdf_path} to SVG using pdftocairo")
        cmd = f"pdftocairo -svg {pdf_path} {svg_path}"
        subprocess.run(cmd, shell=True, check=True)
        return svg_path

    def convert_pdf_to_svg(self, pdf_path: Path, svg_path: Path) -> Path:
        if "pdfcairo" in self.backends:
            fn = self.convert_pdf_to_svg_pdftocairo
        else:
            fn = self.convert_pdf_to_svg_pdftocairo
        return fn(pdf_path, svg_path)

    def convert_svg_to_pdf_cairosvg(self, svg_path: Path, pdf_path: Path) -> Path:
        logger.info(f"Converting {svg_path} to PDF using CairoSVG")
        cmd = f"cairosvg -f pdf -o {pdf_path} {svg_path}"
        subprocess.run(cmd, shell=True, check=True)
        return pdf_path

    def convert_svg_to_pdf(self, svg_path: Path, pdf_path: Path) -> Path:
        if "cairosvg" in self.backends:
            fn = self.convert_svg_to_pdf_cairosvg
        else:
            fn = self.convert_svg_to_pdf_cairosvg
        return fn(svg_path, pdf_path)

    def convert_pdfpages_to_pdf_poppler(
        self, pdf_paths: list[Path], pdf_path: Path
    ) -> None:
        logger.info(f"Combining PDF pages to {pdf_path} using Poppler")
        pdf_paths_str = " ".join(str(pdf) for pdf in pdf_paths)
        cmd = f"pdfunite {pdf_paths_str} {pdf_path}"
        subprocess.run(cmd, shell=True, check=True)

    def convert_pdfpages_to_pdf(self, pdf_paths: list[Path], pdf_path: Path) -> None:
        if "poppler" in self.backends:
            fn = self.convert_pdfpages_to_pdf_poppler
        else:
            fn = self.convert_pdfpages_to_pdf_poppler
        return fn(pdf_paths, pdf_path)

    def process(self):
        logger.info(f"Processing {self.inpath}")
        pdfpages_paths = self.convert_pdf_to_pdfpages(self.inpath, self.pdf_t_dir)

        converted_pdfs = []
        for pdf_path in pdfpages_paths:
            logger.info(f"Processing {pdf_path}")
            svg_path = self.svg_q_dir / f"{pdf_path.stem}.svg"
            logger.info(f"Converting {pdf_path} to SVG")
            self.convert_pdf_to_svg(pdf_path, svg_path)
            converted_pdf_path = self.pdf_q_dir / f"{pdf_path.stem}.pdf"
            logger.info(f"Converting {svg_path} to PDF")
            self.convert_svg_to_pdf(svg_path, converted_pdf_path)
            converted_pdfs.append(converted_pdf_path)

        logger.info(f"Combining PDF pages to {self.pdf_q_path}")
        self.convert_pdfpages_to_pdf(sorted(converted_pdfs), self.pdf_q_path)
        print(self.pdf_q_path)


def convert_pdfs(
    inpath: str,
    outdir: str = None,
    dir: bool = False,
    pdf_filters=(),
    svg_filters=(),
    verbose=False,
):
    if verbose:
        logging.basicConfig(level=logging.INFO)
    if outdir is None:
        outdir = Path(inpath).parent
    else:
        outdir = Path(outdir)
        outdir.mkdir(parents=True, exist_ok=True)
    if dir:
        infolder = Path(inpath)
        pdf_paths = list(infolder.glob("*.pdf"))
    else:
        pdf_paths = [Path(inpath)]
    for pdf_path in pdf_paths:
        logger.info(f"Processing {pdf_path}")
        converter = PDF2SVG2PDF(
            pdf_path,
            outdir,
            verbose=verbose,
            pdf_filters=pdf_filters,
            svg_filters=svg_filters,
        )
        converter.process()


def cli():
    fire.core.Display = lambda lines, out: print(*lines, file=out)
    fire.Fire(convert_pdfs)


if __name__ == "__main__":
    cli()
