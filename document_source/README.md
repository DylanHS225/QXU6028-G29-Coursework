# Word document source

The report is authored with python-docx and editable Office Math (OMML), using the ASCII/LaTeX source in report.md. It contains six embedded figures, not page screenshots. Body, headings, captions and native equation text runs specify Arial. Superscript and subscript layout uses native Office elements.

To rebuild after regenerating the figures, install python-docx and lxml, then run:

```sh
python document_source/build_report.py
```

This writes QXU6028_Coursework_Report.docx in the package folder. The script requires the completed figure outputs and the preserved schematic asset. PDF conversion and visual review are separate document checks. The delivered report was rendered and reviewed page by page.
