{ pkgs, ... }: {
  packages = [];
  bootstrap = ''
    mkdir "$out"
    cp -rf ${./.}/* "$out"
    chmod -R u+w "$out"
  '';
}