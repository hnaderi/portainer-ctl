let
  pkgs = import <nixpkgs> { };
in
pkgs.mkShell {
  name = "Portainer controller";
  buildInputs = with pkgs; [
    python
    uv
    ruff
  ];
}
