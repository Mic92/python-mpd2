{
  description = "Development environment for this project";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
    flake-parts.inputs.nixpkgs-lib.follows = "nixpkgs";
    treefmt-nix.url = "github:numtide/treefmt-nix";
    treefmt-nix.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs =
    inputs@{ flake-parts, treefmt-nix, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      imports = [
        treefmt-nix.flakeModule
      ];
      systems = [
        "aarch64-linux"
        "x86_64-linux"
        "aarch64-darwin"
        "x86_64-darwin"
      ];
      perSystem =
        { pkgs, config, ... }:
        {
          treefmt = {
            projectRootFile = "flake.nix";
            programs = {
              ruff.format = true;
              ruff.check = true;
              mypy.enable = true;
              mypy.directories = {
                "." = {
                  modules = [ "mpd" ];
                };
              };
            };
          };

          devShells.default = pkgs.mkShell {
            packages = with pkgs; [
              bashInteractive
              python310
              python311
              python312
              (python313.withPackages (ps: [
                ps.setuptools
                ps.tox
                ps.wheel
                ps.build
              ]))
              python314
              pypy3
              twine
              mypy
              ruff
              config.treefmt.build.wrapper
            ];
          };
        };
    };
}
