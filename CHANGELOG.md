# Changelog

## [0.4.0](https://github.com/dsgt-birdclef/birdclef-2023/compare/app-v0.3.0...app-v0.4.0) (2023-01-28)


### Features

* add commit/ref information to status; luxon for date parsing ([1a4742d](https://github.com/dsgt-birdclef/birdclef-2023/commit/1a4742d757bf58507a6fc3f741be5115409e67c0))
* Add next and live deployments as separate cloudrun instances ([#18](https://github.com/dsgt-birdclef/birdclef-2023/issues/18)) ([972eaf6](https://github.com/dsgt-birdclef/birdclef-2023/commit/972eaf6b7fb37de8e6cd47d4e8bfef07d8bec556))


### Bug Fixes

* do not prefix envvar with VITE at built time ([6486fd6](https://github.com/dsgt-birdclef/birdclef-2023/commit/6486fd6d84e677872e7f210cdd27e351e0eb9cb0))
* import DateTime from luxon instead of default ([f0d5705](https://github.com/dsgt-birdclef/birdclef-2023/commit/f0d57058cb0ecdd279a756128b4eafcb9c7c1638))
* set commit/ref/namespace information in build ([176b759](https://github.com/dsgt-birdclef/birdclef-2023/commit/176b7598c9f4b52db725d6a4641f10b8bb3a025e))

## [0.3.0](https://github.com/dsgt-birdclef/birdclef-2023/compare/app-v0.2.0...app-v0.3.0) (2023-01-28)


### Features

* build docker images based on release tags ([01c941d](https://github.com/dsgt-birdclef/birdclef-2023/commit/01c941dd1c618419d8e798a2fcdc19717943a18c))


### Bug Fixes

* add compose to the docker steps in deploy-site ([fe7dccb](https://github.com/dsgt-birdclef/birdclef-2023/commit/fe7dccb4742126fbe69caa550cacbe22da01700e))
* fix typo in terraform namespace ([1f2d73f](https://github.com/dsgt-birdclef/birdclef-2023/commit/1f2d73f8dfcf3a695e1771a5b20c9411f1fdd4d8))

## [0.2.0](https://github.com/dsgt-birdclef/birdclef-2023/compare/app-v0.1.0...app-v0.2.0) (2023-01-28)


### Features

* add initial configuration for release-please ([cdb0d0c](https://github.com/dsgt-birdclef/birdclef-2023/commit/cdb0d0cea6a852f5f0f5ada1358220811f548f94))


### Bug Fixes

* add known hosts to cloudbuild birdnet ([298313a](https://github.com/dsgt-birdclef/birdclef-2023/commit/298313ab37e99ad581cbc218d231487aa2b96b9d))
