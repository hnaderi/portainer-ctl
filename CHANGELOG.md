# CHANGELOG



## v0.0.1 (2023-09-02)

### Fix

* fix: striped .env file lines ([`2cfd73b`](https://github.com/hnaderi/portainer-ctl/commit/2cfd73bf1483664b9a338b776eba14c194cd4c5a))

* fix: create config and secret does not raise error

config and secret creation is meant to be reproducible, and due to their
immutability, their name can be treated as hashes that won&#39;t change, so
proper use will prevent wrong config/secret ([`96f03ba`](https://github.com/hnaderi/portainer-ctl/commit/96f03ba8c1cc7bfb9b752cae75a3ecaa7c99ca56))

* fix: pctl will return exit code 1 when fails ([`7657ea2`](https://github.com/hnaderi/portainer-ctl/commit/7657ea24fdc327cb73a38146ece627ce804b210f))

* fix: added install git to ci ([`db4ec84`](https://github.com/hnaderi/portainer-ctl/commit/db4ec84b5428582e462565ce173a3a83fdc70915))

### Unknown

* Changed CI release job ([`e8d6233`](https://github.com/hnaderi/portainer-ctl/commit/e8d6233f2f49960e72eb5d1c95b3a0bc1c480b81))

* Fixed CI publish job ([`fb1a97f`](https://github.com/hnaderi/portainer-ctl/commit/fb1a97f5135f42b9c6c5fe3bb00a4024fb09bf92))

* Merge pull request #2 from hnaderi/ci

Add CI/CD ([`b0604ec`](https://github.com/hnaderi/portainer-ctl/commit/b0604ec97b1c83cf4532f704d64b45f8aa55b494))

* Added github actions workflows ([`c3f5ddf`](https://github.com/hnaderi/portainer-ctl/commit/c3f5ddf8f5ddef0cf890cc183fcd90ee7b7f9298))

* Merge pull request #1 from hnaderi/packaging

Packaging ([`9f44b4e`](https://github.com/hnaderi/portainer-ctl/commit/9f44b4e1516b1978dea804c1f8a8c61d654ae32e))

* Sorted imports ([`a7e50f6`](https://github.com/hnaderi/portainer-ctl/commit/a7e50f6c25064657b5d0c8b844f7d2a0df60b86a))

* Renamed package to portainer_ctl ([`f5dfe1a`](https://github.com/hnaderi/portainer-ctl/commit/f5dfe1a97dd0036e432be75bd54bedd4075ec7e3))

* Refactored cli ([`cf48bf4`](https://github.com/hnaderi/portainer-ctl/commit/cf48bf44ac7b217483fd718d18410e278a67e3d0))

* Poetry packaging ([`48cf2c1`](https://github.com/hnaderi/portainer-ctl/commit/48cf2c1ee6757c0450488d07e601d18dcc944d2c))

* Refactored Portainer client ([`f58b882`](https://github.com/hnaderi/portainer-ctl/commit/f58b8823b59e62c8e5b459f134ea6bf1def4deb6))

* Blacked! ([`d217710`](https://github.com/hnaderi/portainer-ctl/commit/d2177100475e1bca5be1a23487146d79c8c5d5f5))

* Added flake ([`ff8e64e`](https://github.com/hnaderi/portainer-ctl/commit/ff8e64ed11c7a861f20dc47ebe4639c99b47fa10))

* Added --stack-name option ([`b7222e4`](https://github.com/hnaderi/portainer-ctl/commit/b7222e45338c24d5fb408201d463a8a88e4c101e))

* changed config, secret error log ([`fcfb0b9`](https://github.com/hnaderi/portainer-ctl/commit/fcfb0b9a617bb669b3d91a2c5b269134592ccbb1))

* trimmed secret and config names ([`00b2d7c`](https://github.com/hnaderi/portainer-ctl/commit/00b2d7ce0406cc067bbd0c65dfd52c2af09ecaa2))

* Added stripping to stack name normalization ([`dc73b21`](https://github.com/hnaderi/portainer-ctl/commit/dc73b21b5f0e05264e24c01283aabf51e82a9a2f))

* Normalized stack names to lowercase ([`46f4e1b`](https://github.com/hnaderi/portainer-ctl/commit/46f4e1b7f8802f312e49ee540b3910efbc41c074))

* Added support for API tokens ([`74d9675`](https://github.com/hnaderi/portainer-ctl/commit/74d967588ddd640a217eb5d66610049e6d3cb452))

* added deploy command usage to readme ([`10d90a8`](https://github.com/hnaderi/portainer-ctl/commit/10d90a8f8fb70dd3fcce7205d6437c3098dbfe26))

* added README.md ([`851c648`](https://github.com/hnaderi/portainer-ctl/commit/851c64849de15365b5a110842dcf48815045e072))

* improve: added url to request errors ([`21cf503`](https://github.com/hnaderi/portainer-ctl/commit/21cf503fdb92902bb5841738da0100b4346e35b5))

* Changed docker image user to root

Changed user to root to enable downstream users to install new packages
like git, ...
As this image is meant for CI usage, not having root access makes it useless. ([`1474672`](https://github.com/hnaderi/portainer-ctl/commit/1474672aff5ff4a0214c198f867bbf4657944296))

* Added gitlab ci ([`89f30a2`](https://github.com/hnaderi/portainer-ctl/commit/89f30a2b16b9585f1f90aa004483515fa011fbda))

* Added error handling ([`6973661`](https://github.com/hnaderi/portainer-ctl/commit/6973661d735a24cafa7606918adcb03beb12ec09))

* Implemented update stack ([`742dc2e`](https://github.com/hnaderi/portainer-ctl/commit/742dc2e44f440b2e4d26dca60feb538f002d8fd2))

* First tested version for deploy ([`0420165`](https://github.com/hnaderi/portainer-ctl/commit/04201656f40765d130e1ac61e7621c614e810963))

* draft for pctl ([`9ae2260`](https://github.com/hnaderi/portainer-ctl/commit/9ae22600a0590b395de9072c91922783ace33cfa))

* Initial commit ([`1de5e49`](https://github.com/hnaderi/portainer-ctl/commit/1de5e4948d20b44d0fffa7ed19bda8c2f3a0641a))
