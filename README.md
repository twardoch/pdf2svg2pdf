# pdf2svg2pdf

**`pdf2svg2pdf` is a powerful command-line tool and Python library designed to convert multi-page PDF documents into Scalable Vector Graphics (SVG), allow for programmatic modifications or filtering of these SVGs, and then reassemble them into a new PDF document.**

This tool facilitates a vector-to-vector workflow, ensuring that the quality and scalability of your graphics are maintained throughout the process. It's particularly useful when you need to make detailed changes to PDF content that are typically easier to perform at the SVG level.

## What it does

At its core, `pdf2svg2pdf` performs the following sequence of operations:

1.  **Splits PDF:** Takes an input multi-page PDF and separates it into individual single-page PDF files.
2.  **PDF to SVG Conversion:** Converts each single-page PDF into an SVG file.
3.  **Modifications (Optional):** This is where the magic happens. While the primary script provides the framework, the `pdf2svg2pdf_classic.py` script (and programmatic usage) allows for applying various filters and modifications to the SVG files (e.g., color changes, optimizations, element manipulation) or even to the initial PDF pages (e.g., converting to grayscale).
4.  **SVG to PDF Conversion:** Converts the (potentially modified) SVG files back into single-page PDF files.
5.  **Merges PDF:** Combines the processed single-page PDFs into a final, new multi-page PDF document.

## Who it's for

This tool is beneficial for:

*   **Developers** working with PDF and SVG formats who need to automate transformations or content manipulation.
*   **Graphic Designers and Technical Users** who need to perform batch modifications on PDF vector content that are difficult with standard PDF editors.
*   Anyone needing to **programmatically clean up, optimize, or alter elements** within PDF documents by leveraging the more accessible structure of SVGs.
*   Users looking to **integrate PDF-to-SVG-to-PDF workflows** into larger document processing pipelines.

## Why it's useful

*   **Unlock PDF Content:** Enables modification of PDF content that is often "locked" or hard to edit directly in PDF format.
*   **Leverage SVG Editability:** SVGs are XML-based and much easier to parse, manipulate, and generate programmatically.
*   **Vector Quality Preservation:** Ensures that graphics remain scalable and high-quality throughout the conversion process.
*   **Automation:** Provides a command-line interface and Python library for automating repetitive PDF transformation tasks.
*   **Filtering & Optimization:** The `pdf2svg2pdf_classic.py` script and library usage allow for powerful filtering, such as:
    *   Optimizing SVGs with `svgo`.
    *   Changing colors or making backgrounds transparent.
    *   Converting PDFs to grayscale before SVG conversion.

## Installation

### 1. Python Package

You can install `pdf2svg2pdf` using pip:

```bash
pip install pdf2svg2pdf
```

### 2. External Dependencies

`pdf2svg2pdf` relies on several external command-line tools for its core functionality. Please ensure they are installed and accessible in your system's PATH.

*   **Poppler Utilities:** Provides `pdfseparate`, `pdfunite`, and `pdftocairo`.
    *   On Debian/Ubuntu: `sudo apt-get update && sudo apt-get install poppler-utils`
    *   On macOS (using Homebrew): `brew install poppler`
    *   On Fedora: `sudo dnf install poppler-utils`
    *   On Windows: Installation can be more complex. Consider using WSL, or finding precompiled binaries for Windows.
*   **CairoSVG:** Provides the `cairosvg` command-line tool for converting SVGs to PDFs.
    *   While `cairocffi` is a Python dependency, the `cairosvg` CLI is also used.
    *   On Debian/Ubuntu: `sudo apt-get install cairosvg` (may also be installed via pip: `pip install CairoSVG` - ensure the CLI tool is in PATH)
    *   On macOS (using Homebrew): `brew install cairo` (CairoSVG might need `pip install CairoSVG`)
    *   On Fedora: `sudo dnf install cairo` (and potentially `pip install CairoSVG`)

### 3. Optional External Dependencies (for `pdf2svg2pdf_classic.py` filters)

For advanced filtering capabilities provided by the `pdf2svg2pdf_classic.py` script, you might need:

*   **Ghostscript (`gs`):** Used by filters like `pdf_grayscale`.
    *   On Debian/Ubuntu: `sudo apt-get install ghostscript`
    *   On macOS (using Homebrew): `brew install ghostscript`
    *   On Fedora: `sudo dnf install ghostscript`
*   **SVGO (`svgo`):** A Node.js tool for optimizing SVG files, used by the `svgo` filter.
    *   Requires Node.js and npm.
    *   Installation: `npm install -g svgo`

## How to Use

### Command-Line Interface (CLI)

#### Main tool (`pdf2svg2pdf`)

The primary CLI tool is `pdf2svg2pdf`, which is ideal for straightforward PDF-to-SVG-to-PDF conversions.

*   **Convert a single PDF file:**
    ```bash
    pdf2svg2pdf /path/to/your/input.pdf --outdir /path/to/output_directory
    ```
    The processed PDF will be saved as `<output_directory>/<input_filename_stem>-q.pdf`. Intermediate files (split PDFs, SVGs) will be stored in subdirectories within the output directory.

*   **Process all PDF files in a directory:**
    ```bash
    pdf2svg2pdf /path/to/input_directory --dir --outdir /path/to/output_directory
    ```
    This will process each `*.pdf` file in the input directory, creating a corresponding `-q.pdf` in the output directory.

*   **Verbose mode (for more detailed logging):**
    ```bash
    pdf2svg2pdf input.pdf --outdir output --verbose
    ```

*   **Specify conversion backends (optional):**
    The tool automatically selects backends. If needed, you can specify them:
    ```bash
    pdf2svg2pdf input.pdf --outdir output --backends fitz pdfcairo cairosvg
    ```
    Available backends: `fitz` or `poppler` for PDF splitting, `pdfcairo` for PDF-to-SVG, `cairosvg` for SVG-to-PDF.

#### Classic tool (`pdf2svg2pdf_classic.py`) for Advanced Filtering

For more advanced use cases, especially those involving PDF or SVG filters, you can use the `pdf2svg2pdf_classic.py` script directly.

*   **Basic usage (similar to the main tool but invokes the classic script):**
    ```bash
    python -m pdf2svg2pdf.pdf2svg2pdf_classic /path/to/input.pdf --outdir /path/to/output
    ```

*   **Using SVG filters:**
    Apply `svgo` optimization and make white backgrounds transparent:
    ```bash
    python -m pdf2svg2pdf.pdf2svg2pdf_classic input.pdf --outdir output \
           --svg_filters "svgo,svg_transparent_white"
    ```
    *Note: Filters are passed as comma-separated strings. Available built-in SVG filters include `svgo`, `svg_transparent_white`, `svg_fill0`, `svg_fill1`.*

*   **Using PDF filters:**
    Convert the PDF to grayscale before processing:
    ```bash
    python -m pdf2svg2pdf.pdf2svg2pdf_classic input.pdf --outdir output \
           --pdf_filters "pdf_grayscale"
    ```
    *Note: Available built-in PDF filters include `pdf_grayscale`.*

### Programmatic Usage (Python Library)

You can integrate `pdf2svg2pdf` into your Python projects.

#### Using `PDF2SVG2PDF` (Main module)

This class provides the core conversion workflow.

```python
from pdf2svg2pdf import PDF2SVG2PDF
import logging

# Optional: Enable verbose logging
# logging.basicConfig(level=logging.INFO)

try:
    converter = PDF2SVG2PDF(
        inpath="my_document.pdf",
        outdir="processed_output"
        # verbose=True # another way to enable verbosity for this instance
        # backends=["poppler", "pdfcairo", "cairosvg"] # Optional: specify backends
    )
    output_pdf_path = converter.process() # process() now returns the path
    print(f"Processed PDF saved to: {output_pdf_path}")

except Exception as e:
    print(f"An error occurred: {e}")
    # Add more specific error handling for missing dependencies if needed
    # e.g., check for FileNotFoundError if external tools are missing
```

#### Using `pdf2svg2pdf_classic.pdf2svg2pdf` (for filters)

To leverage the filtering capabilities programmatically, use the functions from the `classic` module.

```python
from pdf2svg2pdf.pdf2svg2pdf_classic import (
    pdf2svg2pdf as classic_pdf2svg2pdf,
    svgo,  # Example SVG filter
    pdf_grayscale, # Example PDF filter
    svg_transparent_white # Another SVG filter
)
import logging

# Optional: Enable verbose logging for the underlying processes
# logging.basicConfig(level=logging.INFO) # Note: classic script uses logging differently

# Define your filters - they must be functions
# For svgo, it's already defined. For custom string-based filters in CLI,
# the script uses eval, but in library use, pass the functions directly.

my_svg_filters = [
    svgo,
    svg_transparent_white
    # lambda svg_content: svg_content.replace("fill:#000000", "fill:#FF0000") # custom filter example
]
my_pdf_filters = [
    pdf_grayscale
]

try:
    # The classic pdf2svg2pdf function processes and prints the output path
    # It doesn't return it directly in the same way as the PDF2SVG2PDF class method.
    # We'll need to construct the expected output path or capture stdout if needed for automation.
    input_pdf = "my_document.pdf"
    output_dir = "processed_classic_output"

    classic_pdf2svg2pdf(
        inpath=input_pdf,
        outdir=output_dir,
        svg_filters=my_svg_filters,
        pdf_filters=my_pdf_filters
    )
    # The output path is printed to stdout by the classic_pdf2svg2pdf function.
    # Example: print(f"{outdir / f'{inpath.stem}-q.pdf'}")
    # So, you'd typically know it's: output_dir / (Path(input_pdf).stem + "-q.pdf")

    print(f"Classic processing complete. Check '{output_dir}' for results.")

except Exception as e:
    print(f"An error occurred during classic processing: {e}")
```

---
## Technical Details

This section provides a deeper dive into how `pdf2svg2pdf` works internally and outlines guidelines for coding and contributing to the project.

### How the Code Works Precisely

#### Main Tool: `pdf2svg2pdf.py`

The primary logic is encapsulated within the `PDF2SVG2PDF` class in `src/pdf2svg2pdf/pdf2svg2pdf.py`.

1.  **Initialization (`__init__`):**
    *   Sets up input and output paths, creating necessary output subdirectories (`<stem>-pdf-t`, `<stem>-svg-q`, `<stem>-pdf-q`) if they don't exist.
    *   Determines which backends to use for conversion steps. Default backends are `["poppler", "pdfcairo", "cairosvg"]`. Users can override this.
    *   Configures basic logging based on the `verbose` flag.

2.  **Processing Workflow (`process` method):**
    *   **Split PDF to Pages:**
        *   Calls `convert_pdf_to_pdfpages(self.inpath, self.pdf_t_dir)`.
        *   This method uses `convert_pdf_to_pdfpages_fitz` if `"fitz"` is in `self.backends` (or by default if Poppler isn't specified first). This uses `PyMuPDF` (Fitz) to create a new single-page PDF for each page of the input document.
        *   Alternatively, it uses `convert_pdf_to_pdfpages_poppler` if `"poppler"` is preferred. This shells out to the `pdfseparate` command-line tool.
        *   The resulting single-page PDFs are stored in the `<stem>-pdf-t` directory.
    *   **Per-Page Conversion Loop:** Iterates through each single-page PDF.
        *   **PDF to SVG:**
            *   Calls `convert_pdf_to_svg(pdf_page_path, svg_output_path)`.
            *   This currently defaults to `convert_pdf_to_svg_pdftocairo`, which uses the `pdftocairo -svg <pdf> <svg>` command-line tool. The output SVG is saved in `<stem>-svg-q`.
        *   **SVG to PDF:**
            *   Calls `convert_svg_to_pdf(svg_path, pdf_output_path)`.
            *   This currently defaults to `convert_svg_to_pdf_cairosvg`, which uses the `cairosvg -f pdf -o <pdf> <svg>` command-line tool. The output PDF for the page is saved in `<stem>-pdf-q`.
    *   **Combine PDF Pages:**
        *   Calls `convert_pdfpages_to_pdf(list_of_processed_page_pdfs, self.pdf_q_path)`.
        *   This currently defaults to `convert_pdfpages_to_pdf_poppler`, which uses the `pdfunite` command-line tool to merge all processed single-page PDFs (from `<stem>-pdf-q`) into the final output file: `<outdir>/<stem>-q.pdf`.
    *   The final output path is printed to standard output.

#### Classic Tool: `pdf2svg2pdf_classic.py`

The `pdf2svg2pdf_classic.py` script offers a similar pipeline but with a focus on filtering capabilities and parallel processing.

1.  **Folder Creation:** Sets up temporary directories similar to the main tool.
2.  **PDF Splitting (`separate_pdf`):**
    *   If `pdf_filters` are provided:
        *   The input PDF is read into bytes.
        *   Each function in `pdf_filters` is applied sequentially to the PDF byte stream. Example: `pdf_grayscale` uses Ghostscript (`gs`) via `subprocess.run()` to convert PDF bytes to grayscale.
        *   The (potentially modified) PDF bytes are written to a temporary file, which is then split into pages using `PyMuPDF` (Fitz) via `separate_pdf_with_filters`.
    *   If no `pdf_filters` are provided:
        *   It uses `separate_pdf_no_filters`, which shells out to `pdfseparate`.
3.  **Parallel Page Processing (`chain_convert` executed by `ProcessPoolExecutor`):**
    *   For each single-page PDF generated:
        *   **PDF to SVG:** `convert_pdf_to_svg` calls `pdftocairo -svg`.
        *   **SVG Filtering:** If `svg_filters` are provided:
            *   The SVG content is read from the file.
            *   Each function in `svg_filters` is applied sequentially to the SVG content string.
                *   Filters can be predefined functions (e.g., `svgo` which calls the `svgo` CLI, `svg_transparent_white` which uses regex) or custom functions.
                *   If filters are passed as strings via CLI, `eval()` is used to resolve them (e.g., `eval(f"lambda svg: svg{svg_filter}")` for simple attribute changes, or just `eval(svg_filter)` for named functions).
            *   The modified SVG content is written back to the SVG file.
        *   **SVG to PDF:** `convert_svg_to_pdf` calls `cairosvg -f pdf`.
4.  **PDF Uniting (`unite_pdfs`):**
    *   The processed single-page PDFs are merged using `pdfunite`.
5.  **Output:** The path to the final combined PDF is printed to standard output.

### Rules of Coding and Contributing

We welcome contributions to `pdf2svg2pdf`! Please follow these guidelines to help maintain code quality and consistency.

#### Coding Style

*   **Formatting:** This project uses [Black](https://github.com/psf/black) for code formatting and [isort](https://pycqa.github.io/isort/) for import sorting.
    *   Please format your code with Black before committing.
    *   Ensure imports are sorted with isort.
*   **Linting:** [Flake8](https://flake8.pycqa.org/en/latest/) is used for linting.
    *   The configuration is in `setup.cfg` (e.g., `max_line_length = 88`, ignoring `E203`, `W503` for Black compatibility).
*   **Pre-commit Hooks:** The project is set up with pre-commit hooks that automatically run Black, isort, and Flake8, among other checks.
    *   Install pre-commit: `pip install pre-commit`
    *   Set up the hooks in your local clone: `pre-commit install`
    *   This will help ensure your contributions meet the style guidelines.

#### Testing

*   Tests are located in the `tests/` directory.
*   This project uses [pytest](https://docs.pytest.org/) for running tests and [pytest-cov](https://pytest-cov.readthedocs.io/) for coverage.
*   **Run tests:** `pytest`
*   **Run tests with coverage:** `pytest --cov=src`
*   Please write tests for any new features or bug fixes you introduce. Aim for good test coverage.

#### Contribution Process

1.  **Fork the Repository:** Create your own fork of the [twardoch/pdf2svg2pdf](https://github.com/twardoch/pdf2svg2pdf) repository on GitHub.
2.  **Create a Branch:** Create a new branch in your fork for your changes (e.g., `git checkout -b feature/my-new-feature` or `bugfix/issue-123`).
3.  **Make Your Changes:** Implement your feature or bug fix.
4.  **Write/Update Tests:** Add or modify tests to cover your changes.
5.  **Ensure Checks Pass:**
    *   Run tests locally (`pytest`).
    *   Ensure pre-commit hooks pass (or run `black .`, `isort .`, `flake8` manually).
6.  **Commit Your Changes:** Use clear and descriptive commit messages.
7.  **Push to Your Fork:** Push your branch to your fork on GitHub.
8.  **Submit a Pull Request (PR):** Open a Pull Request from your branch to the `main` branch of the original repository.
    *   Clearly describe the changes you've made and why.
    *   If your PR addresses an existing issue, please reference it (e.g., "Fixes #123").

#### Dependencies

*   **Python Dependencies:** Core Python dependencies are listed in `setup.cfg` under `install_requires`.
*   **External Tool Dependencies:** Be mindful of the external command-line tools required (Poppler, CairoSVG, and optionally Ghostscript, SVGO). If adding functionality that relies on a new external tool, ensure this is well-documented.

#### Documentation

*   The project documentation (including this README) is written in Markdown and processed by [Sphinx](https://www.sphinx-doc.org/) using the [MyST parser](https://myst-parser.readthedocs.io/).
*   Source files for documentation are primarily in the `docs/` directory.
*   If your changes affect user-facing behavior or add new features, please update the relevant parts of the documentation (README.md, and potentially files in `docs/`).
