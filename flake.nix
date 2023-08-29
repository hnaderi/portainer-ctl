{
  description = "Portainer controller development environment";
  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  outputs = { self, flake-utils, nixpkgs }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        python = (pkgs.python3.withPackages
          (ps: with ps; [ black isort pylsp-mypy requests types-requests ]));
      in {
        devShells.default = pkgs.mkShell {
          buildInputs = [ python ];
          packages = [ python ];
        };
      });
}
