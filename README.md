# OCRGazzete Overview

This project aimed to automatically extract trademark images from newspapers and match them with application records in a pre-existing database, while minimizing the error rate in classification. The objective was to achieve an 80% identification rate while maintaining near-perfect accuracy.

## Data Extraction Process
The process is implemented in six steps:

Pre-processing: This involves converting the PDF files of the newspapers into readable text and image files using Optical Character Recognition (OCR).
Image extraction: All trademark images are extracted from the pre-processed files.
Data extraction: Relevant notice data and metadata are collected for each trademark.
Matching: Each image is matched with its corresponding notice.
Accuracy computation: The accuracy and identification rates are calculated.
Database integration: The final results are integrated into the existing database.
Pre-Processing
The pre-processing phase involves transforming image-only PDF files into searchable text PDF files. Abbyy Finereader 15 is the tool used to generate these OCR files due to its capability to process old newspapers and preserve the original structure. After pre-processing, text and image areas are classified with different color frames.

### Data Extraction
After identifying a paragraph as a notice, the next step is to extract the relevant information such as application number, class number, country, city, applicant, and application date. An external library is used to extract the dates from the text.

### Matching Images and Notices
The matching algorithm leverages the structure and rules of the newspaper to pair each notice with its corresponding trademark image. The algorithm scans each notice and finds a list of candidate images that meet certain conditions based on the layout of the newspaper.

### Optimization and Verification
The described procedure has room for further optimization. The extract function's first step involves obtaining a list of all unmatched rows. If a second extract function run is applied, some unmatched notices from the first run might find a match. To maximize the identification rate with a minimal impact on accuracy, two verification levels are created. Verification level 1 follows the described procedure, whereas verification level 2 uses pattern matching, reducing the confidence in the matches but improving the identification rate.

## Getting Started
To use this project, follow the instructions in the documentation to set up the necessary software and libraries, such as Abbyy Finereader 15 and the external date extraction library. Then, use the scripts provided in this repository to run the image and data extraction, matching, and verification steps.

## Contact
For further questions or suggestions, feel free to contact us via the repository issue tracker or the provided contact information.
