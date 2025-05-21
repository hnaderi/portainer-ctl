let
  pkgs = import <nixpkgs> { };
  python = pkgs.python3.withPackages (ps: with ps; [ pylsp-mypy ]);
in pkgs.mkShell {
  name = "Portainer controller";
  buildInputs = [ python pkgs.uv ];
}
