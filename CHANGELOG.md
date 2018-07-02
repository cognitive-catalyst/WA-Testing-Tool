# Changelog
All notable changes to this project will be documented in this file.

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
