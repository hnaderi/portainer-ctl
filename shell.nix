let
  pkgs = import <nixpkgs> { };
  python = pkgs.python3.withPackages
    (ps: with ps; [ pylsp-mypy requests rich rich-argparse black ]);
in pkgs.mkShell {
  name = "Portainer controller";
  buildInputs = [ python pkgs.uv ];
}
