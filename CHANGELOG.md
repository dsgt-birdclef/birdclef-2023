# Changelog

## [0.6.0](https://github.com/dsgt-birdclef/birdclef-2023/compare/app-v0.5.0...app-v0.6.0) (2023-03-05)


### Features

* add ansible for installing node18 ([655ada8](https://github.com/dsgt-birdclef/birdclef-2023/commit/655ada8a11c867542a1ef8be120e59264b0d0bcd))
* add ansible for installing tensorflow build deps ([695d6fd](https://github.com/dsgt-birdclef/birdclef-2023/commit/695d6fd7b995c66b99a2c1f416300625abbe56df))
* add documentation for running luigi tasks ([9a80b20](https://github.com/dsgt-birdclef/birdclef-2023/commit/9a80b20b7a858f505770ef25925793e87aa677bf))
* Add skeleton for torch pcm dataset ([016fb4b](https://github.com/dsgt-birdclef/birdclef-2023/commit/016fb4b731832af11f92dfe22602bc823dd1820a))
* Add tensorflow and tensorboard to the environment ([90d7e8c](https://github.com/dsgt-birdclef/birdclef-2023/commit/90d7e8c554d63f694c24c58c73811b2cc9821383))
* added static plots for embedding-knn page ([#55](https://github.com/dsgt-birdclef/birdclef-2023/issues/55)) ([b49d564](https://github.com/dsgt-birdclef/birdclef-2023/commit/b49d564afc97bf6c2dafeb8fe787c29c6e9f2da7))
* convert birdnet from tensorflow to onnx ([639bf7d](https://github.com/dsgt-birdclef/birdclef-2023/commit/639bf7d5460bee6c1f424b1fedc4c51bb194472a))
* notebook for Bird net weights ([#38](https://github.com/dsgt-birdclef/birdclef-2023/issues/38)) ([a335631](https://github.com/dsgt-birdclef/birdclef-2023/commit/a3356316004dfd67697c04658a0d69d8a0dc1c82))
* refactor documentation into smaller fragments ([4e6533d](https://github.com/dsgt-birdclef/birdclef-2023/commit/4e6533d67cf1b44785b3b5fdbe42c8e91dd35a15))
* update requirements for python 3.10 ([a50ae73](https://github.com/dsgt-birdclef/birdclef-2023/commit/a50ae73f7be28bfd0229475241722b1335b5da66))
* Updated Notebook for Exploring Weight Conversions ([#45](https://github.com/dsgt-birdclef/birdclef-2023/issues/45)) ([f465ab7](https://github.com/dsgt-birdclef/birdclef-2023/commit/f465ab7c6f8fbdfbb99e75dfbc7a1442b6171bd0))


### Bug Fixes

* add dependencies for running librosa ([2776af1](https://github.com/dsgt-birdclef/birdclef-2023/commit/2776af155dff0693491ab9f9fa053d7571652604))
* link system node to conda node if exists ([8f43860](https://github.com/dsgt-birdclef/birdclef-2023/commit/8f43860a00045faaf4bfb334af3e65f16258b291))
* prevent changelog from being included in pre-commit checks ([e3ba5a9](https://github.com/dsgt-birdclef/birdclef-2023/commit/e3ba5a91b735381ce57315bd6f29e128de7924ca))
* use find_package in setup.py ([5cd7bb8](https://github.com/dsgt-birdclef/birdclef-2023/commit/5cd7bb8e638c6df4e3563e29e8ce66195f2c8f5a))

## [0.5.0](https://github.com/dsgt-birdclef/birdclef-2023/compare/app-v0.4.0...app-v0.5.0) (2023-02-15)


### Features

* add docker image for luigi scheduler ([12eecb9](https://github.com/dsgt-birdclef/birdclef-2023/commit/12eecb94736de9580417d1789d1858459496fd6c))
* add example cloud batch job ([e0c08c6](https://github.com/dsgt-birdclef/birdclef-2023/commit/e0c08c647a80a217d089322db36cb99b9d24f9f3))
* add initial app container using kaggle gpu image ([174ac93](https://github.com/dsgt-birdclef/birdclef-2023/commit/174ac93941032beb34cfe4012149776c52ca7e02))
* add teraform and ansible skeleton for setting up luigid ([77dd65a](https://github.com/dsgt-birdclef/birdclef-2023/commit/77dd65aa1548ce9ccee08d32f624b8608de765f5))
* build luigi docker container on cloudbuild ([19b7b13](https://github.com/dsgt-birdclef/birdclef-2023/commit/19b7b13eae71324d3759ddd9a3f3973e4f7bfb78))
* configure luigi vm with luigi docker image ([b4dafc0](https://github.com/dsgt-birdclef/birdclef-2023/commit/b4dafc09a9a842060cd32a827ed7b84bca3ca737))
* reorganize configuration files (aside from docker) into conf ([ff80bda](https://github.com/dsgt-birdclef/birdclef-2023/commit/ff80bda8ac1a2c410d073119ca46f8bc6da60b4f))


### Bug Fixes

* install during docker startup ([1c3fb01](https://github.com/dsgt-birdclef/birdclef-2023/commit/1c3fb018001dadbaf664231b2cef3d16c489bf6a))
* remove pip-tools from requirements ([f1e3d93](https://github.com/dsgt-birdclef/birdclef-2023/commit/f1e3d939d01e595ac0c7504bc630f8846df1d88d))

## [0.4.0](https://github.com/dsgt-birdclef/birdclef-2023/compare/app-v0.3.0...app-v0.4.0) (2023-01-28)

### Features

- add commit/ref information to status; luxon for date parsing ([1a4742d](https://github.com/dsgt-birdclef/birdclef-2023/commit/1a4742d757bf58507a6fc3f741be5115409e67c0))
- Add next and live deployments as separate cloudrun instances ([#18](https://github.com/dsgt-birdclef/birdclef-2023/issues/18)) ([972eaf6](https://github.com/dsgt-birdclef/birdclef-2023/commit/972eaf6b7fb37de8e6cd47d4e8bfef07d8bec556))

### Bug Fixes

- do not prefix envvar with VITE at built time ([6486fd6](https://github.com/dsgt-birdclef/birdclef-2023/commit/6486fd6d84e677872e7f210cdd27e351e0eb9cb0))
- import DateTime from luxon instead of default ([f0d5705](https://github.com/dsgt-birdclef/birdclef-2023/commit/f0d57058cb0ecdd279a756128b4eafcb9c7c1638))
- set commit/ref/namespace information in build ([176b759](https://github.com/dsgt-birdclef/birdclef-2023/commit/176b7598c9f4b52db725d6a4641f10b8bb3a025e))

## [0.3.0](https://github.com/dsgt-birdclef/birdclef-2023/compare/app-v0.2.0...app-v0.3.0) (2023-01-28)

### Features

- build docker images based on release tags ([01c941d](https://github.com/dsgt-birdclef/birdclef-2023/commit/01c941dd1c618419d8e798a2fcdc19717943a18c))

### Bug Fixes

- add compose to the docker steps in deploy-site ([fe7dccb](https://github.com/dsgt-birdclef/birdclef-2023/commit/fe7dccb4742126fbe69caa550cacbe22da01700e))
- fix typo in terraform namespace ([1f2d73f](https://github.com/dsgt-birdclef/birdclef-2023/commit/1f2d73f8dfcf3a695e1771a5b20c9411f1fdd4d8))

## [0.2.0](https://github.com/dsgt-birdclef/birdclef-2023/compare/app-v0.1.0...app-v0.2.0) (2023-01-28)

### Features

- add initial configuration for release-please ([cdb0d0c](https://github.com/dsgt-birdclef/birdclef-2023/commit/cdb0d0cea6a852f5f0f5ada1358220811f548f94))

### Bug Fixes

- add known hosts to cloudbuild birdnet ([298313a](https://github.com/dsgt-birdclef/birdclef-2023/commit/298313ab37e99ad581cbc218d231487aa2b96b9d))
