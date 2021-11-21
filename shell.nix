let
  pkgs = import <nixpkgs> {};
in
  with pkgs;
  pkgs.mkShell {
    name = "portainer-bot";
    buildInputs = [ (
      python3.withPackages (
        ps: with ps; [ requests ]
      )
    )
      python-language-server
   ];
  }
