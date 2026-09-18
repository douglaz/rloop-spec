{
  # Dev shell for this specification set: the Lean toolchain ADR-0002 relies on
  # for `tools/formal/`, plus what the existing gates and a Mathlib checkout need.
  #
  # Lean comes from nixpkgs rather than elan so the version is pinned by
  # flake.lock and the binaries run on NixOS unpatched. Mathlib must match this
  # Lean version exactly: pin it to the Mathlib tag named `v<lean version>`
  # (`lean --version` in this shell prints it) or `lake` rebuilds Mathlib from
  # source instead of fetching its cache.
  description = "rloop specification gates and Lean toolchain";

  # Pinned to an exact revision: nixos-unstable at 2026-09-11 (eaad089) ships a lean4
  # whose install step writes to /usr/local and has no binary cache entry, so the
  # shell built Lean from source and then failed. This revision has 4.30.0 cached.
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/aff8a0b28396750446e5537a96461bc4facdb287";

  outputs = { self, nixpkgs }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forAll = f: nixpkgs.lib.genAttrs systems (system: f nixpkgs.legacyPackages.${system});
    in {
      devShells = forAll (pkgs: {
        default = pkgs.mkShell {
          packages = with pkgs; [
            lean4        # lean + lake
            python3      # tools/check_*.py
            git          # lake fetches dependencies over git
          ];
        };
      });

      # `nix flake check` runs the same gates CI does, the Lean build included.
      checks = forAll (pkgs: {
        # runCommandCC, not runCommand: lake compiles the gate executable's C output.
        gates = pkgs.runCommandCC "rloop-spec-gates"
          { nativeBuildInputs = [ pkgs.python3 pkgs.bash pkgs.lean4 ]; } ''
          export HOME="$TMPDIR"
          cp -r ${self} src && chmod -R u+w src && cd src
          bash tools/check-all.sh
          touch $out
        '';
      });
    };
}
