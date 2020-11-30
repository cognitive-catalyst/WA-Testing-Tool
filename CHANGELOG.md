# Changelog
All notable changes to this project will be documented in this file.

## 2020-11-12
### Changed
- Pass Watson Assistant system_settings to test workspaces

## 2020-04-10
### Changed
- validateWS.py is now moved to `log_analytics` folder.
- `waObjects.py` is extracted from that module to provide workspace parsing logic, usable in other modules including analytics

## 2020-01-15
### Added
- [Log extraction and basic analysis](log_analytics/README.md) capabilities in `log_analytics` folder.

## 2019-12-02
### Added
- Configurable k-fold union output file name

## 2019-11-15
### Added
- Support for testing Natural Language Classifier models

## 2019-10-28
### Removed
- Support for username/password authentication. (Watson APIs require API key authentication)

## 2019-09-30
### Added
- Generates confusion matrix in k-fold and blind modes

## 2019-09-26
### Added
- Default values for most configuration values.  Configuration effort is greatly reduced.

## 2019-09-23
### Added
- Utility for extracting conversation logs and utterances based on a given dialog node.

## 2019-09-03
### Updated
- [Static analysis utilities](validate_workspace/README.md) for conversation dialog evaluation.

## 2019-07-10
### Added
- Intent metrics include F1 score.

## 2019-06-21
### Added
- Support for IAM API key

## 2019-06-20
### Added
- [Static analysis utilities](validate_workspace/README.md) for conversation dialog evaluation.

## 2018-07-09
### Added
- Support optional partial credit intent tables

## 2018-07-03
### Added
- Support local workspace JSON as training input

## 2018-06-25
### Added
- Added intent metrics generation script

## 2018-06-14
### Added
- Made service base URL configurable

## 2018-05-21
### Added
- Refactored training input to only use workspace ID

## 2018-05-09
### Added
- Test cases for three modes and all sub-scripts are provided along with testing resources

## 2018-05-04
### Added
- Handling exception by cleaning out workspaces optionally after training phase.
- Exposed maximum test rate and weight mode parameters.

## 2018-04-30
### Fixed
- Allowed intents with confidence less than 0.2 to be returned.

### Added
- Calculate precision using different weighting configuration.
- Highlight confidence threshold on the precision curve figure.
- Union all folds test output as `kfold-test-out-union.csv`.

## 2018-04-13
### Added
- Intent description generation script is provided in [subfolder](intent-description).

## 2018-04-13
### Fixed
- Reserved entities can be imported to workspaces.

## 2018-04-12
### Added
- Coroutine-based concurrent testing is provided in sub-script.
