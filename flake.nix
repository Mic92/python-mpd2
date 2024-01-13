{
  description = "Development environment for this project";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
  };

  outputs = inputs@{ flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } ({ lib, ... }: {
      systems = lib.systems.flakeExposed;
      perSystem = { pkgs, ... }: {
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            bashInteractive
            python38
            python39
            python310
            (python311.withPackages(ps: [ps.setuptools ps.tox ps.wheel]))
            python312
            pypy3
            twine
          ];
          shellHook = ''
            # breaks python36/python37
            unset _PYTHON_SYSCONFIGDATA_NAME
          '';
        };
      };
    });
}
