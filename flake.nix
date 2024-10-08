{
  description = "A customizable and extensible shell";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

    # «https://github.com/nix-systems/nix-systems»
    systems.url = "github:nix-systems/default-linux";
  };

  outputs = {
    nixpkgs,
    self,
    systems,
  }: let
    genSystems = nixpkgs.lib.genAttrs (import systems);
    pkgs = genSystems (system: import nixpkgs {inherit system;});
  in {
    packages = genSystems (system: let
      inherit (pkgs.${system}) callPackage;
    in {
      default = callPackage ./default.nix {};
      evolution-tray = self.packages.${system}.default;
    });
  };
}
