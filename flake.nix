{
  description = "Portainer controller development environment";

  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  inputs.poetry2nix = {
    url = "github:nix-community/poetry2nix";
    inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        inherit (poetry2nix.legacyPackages.${system})
          mkPoetryApplication mkPoetryEnv;
        pkgs = nixpkgs.legacyPackages.${system};

        python = pkgs.python3.withPackages (ps: with ps; [ pylsp-mypy ]);
        poetry = poetry2nix.packages.${system}.poetry;

      in {
        packages = {
          pctl = mkPoetryApplication {
            projectDir = self;
            inherit python;
          };
          default = self.packages.${system}.pctl;
        };

        devShells.default = pkgs.mkShell { packages = [ poetry python ]; };
      });
}
