# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.9.2](https://github.com/apburnes/make-cveasy/compare/v0.9.1...v0.9.2) (2026-01-26)


### Bug Fixes

* Format codebase with ruff and add ruff check to ci ([#35](https://github.com/apburnes/make-cveasy/issues/35)) ([ad177a7](https://github.com/apburnes/make-cveasy/commit/ad177a701c2e2cc22897b91ec9824a6408ad1cd6))

## [0.9.1](https://github.com/apburnes/make-cveasy/compare/v0.9.0...v0.9.1) (2026-01-26)


### Bug Fixes

* **ci:** Remove legacy pypi repo url from publish workflow ([#33](https://github.com/apburnes/make-cveasy/issues/33)) ([5d6b572](https://github.com/apburnes/make-cveasy/commit/5d6b57279a4d696627fb497479bec7d50c06b771))

## [0.9.0](https://github.com/apburnes/make-cveasy/compare/v0.8.0...v0.9.0) (2026-01-26)


### Features

* **ci:** Add publish workflow to pypi ([#31](https://github.com/apburnes/make-cveasy/issues/31)) ([b1a042f](https://github.com/apburnes/make-cveasy/commit/b1a042f531dc43b7888ca77fb94f7c71778f8630))

## [0.8.0](https://github.com/apburnes/make-cveasy/compare/v0.7.0...v0.8.0) (2026-01-26)


### Features

* **docs:** Refactor README to be more concise ([#28](https://github.com/apburnes/make-cveasy/issues/28)) ([46341e3](https://github.com/apburnes/make-cveasy/commit/46341e3deafa3a440dc535532c56ce816afb2778))

## [0.7.0](https://github.com/apburnes/make-cveasy/compare/v0.6.1...v0.7.0) (2026-01-25)


### Features

* Improve CLI performance and command caching ([#26](https://github.com/apburnes/make-cveasy/issues/26)) ([5f92c79](https://github.com/apburnes/make-cveasy/commit/5f92c795b9db3cae93fc2e58a6ec7f1ff116a8ef))

## [0.6.1](https://github.com/apburnes/make-cveasy/compare/v0.6.0...v0.6.1) (2026-01-25)


### Bug Fixes

* **ci:** Release Please to update uv.lock file version ([#23](https://github.com/apburnes/make-cveasy/issues/23)) ([bf50f4a](https://github.com/apburnes/make-cveasy/commit/bf50f4af0e1cbbe5f3b510de53ae6cb03f7c295f))
* **ci:** Release Please update with uv.lock action job ([#25](https://github.com/apburnes/make-cveasy/issues/25)) ([c5c74f3](https://github.com/apburnes/make-cveasy/commit/c5c74f369740b77bb42d1a4b10f2c758fb9dacbb))

## [0.6.0](https://github.com/apburnes/make-cveasy/compare/v0.5.0...v0.6.0) (2026-01-25)


### Features

* Include spaCy model in published package ([#21](https://github.com/apburnes/make-cveasy/issues/21)) ([55a5027](https://github.com/apburnes/make-cveasy/commit/55a5027087ca01660e7922aab317a15a9c552454))

## [0.5.0](https://github.com/apburnes/make-cveasy/compare/v0.4.0...v0.5.0) (2026-01-25)


### Features

* Add error message if no spaCy model loaded ([#19](https://github.com/apburnes/make-cveasy/issues/19)) ([4fa813b](https://github.com/apburnes/make-cveasy/commit/4fa813b51a93198fc1997d0f73518f4119f0c3a7))

## [0.4.0](https://github.com/apburnes/make-cveasy/compare/v0.3.0...v0.4.0) (2026-01-25)


### Features

* Add cveasy version command ([#17](https://github.com/apburnes/make-cveasy/issues/17)) ([3b662b2](https://github.com/apburnes/make-cveasy/commit/3b662b275f41006bf32a48f3328903e740459acc))

## [0.3.0](https://github.com/apburnes/make-cveasy/compare/v0.2.0...v0.3.0) (2026-01-24)


### Features

* Add cveasy config command to configure environment variables ([#14](https://github.com/apburnes/make-cveasy/issues/14)) ([aa70248](https://github.com/apburnes/make-cveasy/commit/aa70248364b2668c79d39d7527aefa6ddd395840))
* Add spaCy model name to config ([#16](https://github.com/apburnes/make-cveasy/issues/16)) ([6aa276e](https://github.com/apburnes/make-cveasy/commit/6aa276e48a91605a3636d5681a0f90f55c18e62d))
* **ci:** Add test support for python 3.13 ([#15](https://github.com/apburnes/make-cveasy/issues/15)) ([1a9b87a](https://github.com/apburnes/make-cveasy/commit/1a9b87ad3ca265d8246dc943d43dae2991051108))
* Improve the cveasy init generated README instructions ([#12](https://github.com/apburnes/make-cveasy/issues/12)) ([ed4df31](https://github.com/apburnes/make-cveasy/commit/ed4df3170f1aaeab7c12c154676780ba8553dda6))

## [0.2.0](https://github.com/apburnes/make-cveasy/compare/v0.1.0...v0.2.0) (2026-01-22)


### Features

* **ci:** Create GH action to publish to pypi ([#10](https://github.com/apburnes/make-cveasy/issues/10)) ([cd527ba](https://github.com/apburnes/make-cveasy/commit/cd527ba5e090ab2145b2ce8d90478f7859e2f2d1))

## 0.1.0 (2026-01-21)


### Features

* Add cveasy cover-letter command to create application cover letters ([86b2837](https://github.com/apburnes/make-cveasy/commit/86b28370417597a4c13142adfe6866c49c1c081a))
* Add cveasy cover-letter command to create application cover letters ([8e97949](https://github.com/apburnes/make-cveasy/commit/8e97949afe8a60cebb1504ab3d817a9f7d3fd688))
* Add Release Please to CI process ([5c3b505](https://github.com/apburnes/make-cveasy/commit/5c3b5051740bfa624f6eeec466fe9d309ccf0f36))
* Add Release Please to CI process ([0f2033f](https://github.com/apburnes/make-cveasy/commit/0f2033f6bef6763c5aa0dcab73a7aea56e97a266))
* Add slug attribute to model types ([cd7e23a](https://github.com/apburnes/make-cveasy/commit/cd7e23a432e2896550af6e99856a813f24c46e7a))
* Add slug attribute to model types ([49e7ec2](https://github.com/apburnes/make-cveasy/commit/49e7ec209bb24e178d33b10e80b932c185f8465c))
* Add token metering service ([33959ad](https://github.com/apburnes/make-cveasy/commit/33959ad221b20cd25fbc7fb10d13a60a7f5bd999))
* Add token metering service ([329e4b6](https://github.com/apburnes/make-cveasy/commit/329e4b615ee1c3dbeccdc3c3bc1d6848ab36c97b))
* **ci:** Add Github test action ([63ef89a](https://github.com/apburnes/make-cveasy/commit/63ef89a9dd0f32d77c844fa70d27e0b1ac5e2192))
* **ci:** Add Github test action ([5c37e54](https://github.com/apburnes/make-cveasy/commit/5c37e549033eec78a48663112ec8fde5a8a860ac))


### Bug Fixes

* **ci:** Add RELEASE_PLEASE_TOKEN to the release cycle ([4807fe9](https://github.com/apburnes/make-cveasy/commit/4807fe9f62f2a42edb72f9f85ca65371cfeec43c))
* **ci:** Add RELEASE_PLEASE_TOKEN to the release cycle ([44d3e89](https://github.com/apburnes/make-cveasy/commit/44d3e89faea8dcc34c1bfc91983502fc44110eef))

## [0.1.0] - 2025-01-20

### Added
- Initial release of CVEasy CLI tool
- Project-based structure for managing resume data
- AI-powered resume generation using OpenAI, Anthropic, or OpenRouter
- Job application management with customized resumes
- Quality checks with keyword and skills matching
- Resume import from PDF or DOCX files
- Export capabilities to PDF or Word documents
- Job description scraping from URLs
- Token usage tracking for AI API calls
