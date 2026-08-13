# Digital Public Goods Standard Compliance Assessment

## Overview

This document provides a detailed assessment of Model_deploy's compliance with the Digital Public Goods Standard. Our goal is to ensure that our project meets the criteria for being recognized as a Digital Public Good, contributing to sustainable development and creating a more equitable world.

## Detailed Assessment

### 1. Relevance to Sustainable Development Goals

**Status: Compliant**

Model_deploy primarily contributes to the following Sustainable Development Goals:

-   **SDG 13: Climate Action**: By providing tools for environmental issue detection and analysis, our project supports efforts to combat climate change and its impacts.
-   **SDG 11: Sustainable Cities and Communities**: Our image classification system can help identify urban environmental issues, contributing to more sustainable urban planning.
-   **SDG 15: Life on Land**: The project's ability to detect issues like deforestation and soil degradation supports the protection of terrestrial ecosystems.

**Evidence**:

-   The CNN model classifies environmental issues such as deforestation, air pollution, and soil degradation.
-   The LLM component provides context and summaries related to these environmental issues.

**Areas for Improvement**:

-   Expand the range of environmental issues detected to cover more SDGs.
-   Develop specific use cases demonstrating the project's impact on SDG targets.

### 2. Use of Approved Open License

**Status: Compliant**

Model_deploy is released under the GNU General Public License v3.0 (GPL-3.0), which is an approved open license.

**Evidence**:

-   The LICENSE file in the root of our repository contains the full text of the GPL-3.0 license.
-   The README.md file clearly states the project's license.

**Areas for Improvement**:

-   Ensure all source code files include a brief license header.
-   Provide clear guidelines for contributors on licensing of submitted code.

### 3. Clear Ownership

**Status: Compliant**

The project is clearly owned and maintained by MapAction.

**Evidence**:

-   The project is hosted under the 223MapAction GitHub organization.
-   The README.md file and other documentation consistently reference MapAction.

**Areas for Improvement**:

-   Include a CODEOWNERS file to clarify responsibility for different parts of the codebase.
-   Provide more information about MapAction and its mission in the project documentation.

### 4. Platform Independence

**Status: Largely Compliant**

Model_deploy is designed to be platform-independent, utilizing technologies that can be deployed across various environments.

**Evidence**:

-   Use of Docker for containerization ensures consistency across different platforms.
-   The core technologies (Python, FastAPI, Celery) are platform-independent.
-   Deployment instructions are provided for different environments.

**Areas for Improvement**:

-   Provide more detailed documentation on deploying to different cloud providers.
-   Ensure all dependencies are cross-platform compatible.

### 5. Documentation

**Status: Largely Compliant**

Model_deploy provides comprehensive documentation covering various aspects of the project.

**Evidence**:

-   Detailed README.md file covering project overview, features, and setup instructions.
-   Developer documentation available at https://223mapaction.github.io/Model_deploy/
-   Inline code comments explaining complex logic.
-   Clear contribution guidelines.

**Areas for Improvement**:

-   Develop user documentation for non-technical users.
-   Create tutorials or guides for common use cases.
-   Ensure all API endpoints are fully documented.

### 6. Mechanism for Extracting Data

**Status: Compliant**

The project provides clear mechanisms for accessing and extracting data.

**Evidence**:

-   FastAPI endpoints for submitting images and retrieving predictions.
-   Database integration for storing and retrieving historical predictions.
-   Use of standard data formats (JSON) for API responses.

**Areas for Improvement**:

-   Implement data export functionality for bulk data retrieval.
-   Provide documentation on data schemas and structures.

### 7. Adherence to Privacy and Applicable Laws
**Status: Compliant**

Model_deploy operates under Map Action's published privacy policy and terms of service, which govern the collection and processing of data across the platform, including this component.

**Evidence:**

A privacy policy has been published and is publicly accessible at: https://map-action.com/politique-de-confidentialite
It covers categories of data collected, purposes of processing, retention periods, data sharing practices, and user rights (access, rectification, deletion), including specific provisions for minors and for anonymous (unregistered) reporting.
The processing operates under Mali's Loi N°2013-015 of 21 May 2013 on the protection of personal data.
Processing activities implemented by Map Action are the subject of a preliminary authorization request filed with Mali's Data Protection Authority (APDP), registered under references DAU-2024-0034/APDP and DAU-2024-0035/APDP.
Terms of Service, including an Acceptable Use Policy and published content-moderation response times, are available at: https://map-action.com/conditions-generales-utilisation
Use of environment variables for sensitive information.
Implementation of CORS middleware for API security.

**Areas for Improvement:**

Implement data anonymization techniques for stored predictions.
Conduct a thorough legal review to ensure alignment with additional international frameworks (e.g., GDPR) where relevant to future regional expansion.

### 8. Adherence to Standards & Best Practices

**Status: Largely Compliant**

Model_deploy follows many software development best practices and standards.

**Evidence**:

-   Use of GitHub Actions for CI/CD.
-   Implementation of unit tests and code coverage reporting.
-   Modular code structure promoting maintainability.
-   Use of type hinting and docstrings for better code readability.

**Areas for Improvement**:

-   Increase test coverage to at least 80%.
-   Implement static code analysis tools in the CI pipeline.
-   Adopt a consistent code style guide (e.g., Black for Python).

### 9. Do No Harm Assessment

**Status: Partially Compliant**

While the project's focus on environmental issues aligns with principles of doing no harm, a formal assessment has not been conducted.

**Evidence**:

-   The project aims to support environmental protection and sustainable development.
-   No obvious harmful applications of the technology have been identified.

**Areas for Improvement**:

-   Conduct a formal "Do No Harm" assessment, considering potential misuse or unintended consequences of the technology.
-   Develop guidelines for ethical use of the Model_deploy system.
-   Implement mechanisms to monitor and prevent potential misuse of the platform.

## Conclusion

Model_deploy demonstrates strong alignment with many aspects of the Digital Public Goods Standard. The project is particularly strong in its relevance to SDGs, open licensing, and technical best practices. However, there are areas for improvement, particularly in privacy compliance and formal harm assessment.

We are committed to addressing these gaps and continuously improving our alignment with the DPG Standard. We welcome community feedback and contributions to help us achieve full compliance and maximize our positive impact as a Digital Public Good.
