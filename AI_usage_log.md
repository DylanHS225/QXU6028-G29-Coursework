# AI usage log

Group number: ____________________

This log discloses the substantial AI contribution visible in the available project chats and files. Group members should review it and add any uses outside those records before signing their contribution statement. Model identifiers for earlier chats were not recorded and are not inferred from the application name.

| Tool or service | Purpose and extent | Retained evidence and verification |
|---|---|---|
| ChatGPT and Codex in earlier L1 work | Interpreted assessment tasks; generated carrier-count integration, mobility calculations, numerical gates, plotting and packaging code; drafted explanatory notes. | Historical L1 code is referenced in `PROVENANCE.md`. The final pipeline recomputes densities and checks closed-form consistency, integration refinement and units. |
| ChatGPT and Codex in earlier L2 work | Generated model-library, paired-channel inversion, model selection, repeat-resampling and plotting code, and explanatory text. | Available L2 code and published commit are recorded in `PROVENANCE.md`. The final analysis preserves signed Hall observations and acquisition order, and repeats selection for 200 samples. |
| ChatGPT and Codex in earlier L3 and blind work | Generated spatial inversion, regularisation comparison, impulse/noise diagnostics and blind-result packaging. | The actual historical blind files and full available blind repository history are retained. Reproduction compares all L1–L3 result fields with the archived submission. |
| Codex during final-report preparation, November 2026 | Read assessment PDFs and lecture slides; inspected available project chats and local code; assembled the report pipeline; generated all numerical figures; drafted and revised the entire English report, self-assessment and process records; built Word/PDF files and checked layout. | `reproduce.py`, `course_methods.py`, `report.md`, numerical diagnostics, run log, source history and the completed report. This includes substantial AI-authored prose, not only grammar correction. Human verification and attribution must be supplied by the group. |
| OpenAI image generation through the built-in image tool | Generated the conceptual two-panel device illustration and revised it after inspection. No numerical charts or data were generated with this tool. | Both prompts, the first image, the corrected asset and error E01. The interface did not return a specific engine identifier; none is asserted here. |
| Web search and primary-source retrieval used through Codex | Located and checked the Vissenberg–Matters and Bittle et al. primary papers cited in the Transfer paragraph. | Bibliographic citations [6] and [7] in the report. The principal methodological authority remains the supplied course material. |

Python, NumPy, pandas, Matplotlib, python-docx, the PDF extraction tools, Git and the document renderer are computational/document tools, rather than additional generative AI services. Their role was calculation, plotting, formatting and verification. Analysis dependency versions are recorded in `requirements.txt` and the generated `evidence/runtime.json`.

AI mistakes detected during this report preparation are described in `AI_error_ledger.md`. No invented member activities, signatures, past errors or pre-release freeze timestamps are supplied. The final report distinguishes the submitted historical blind run from subsequent regular-data analysis.

Other AI uses to be added by group members, if any: ______________________________

Reviewed by: ____________________   Date: ____________________
