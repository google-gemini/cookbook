{ pkgs, ... }: {
  packages = [];
  bootstrap = ''
    mkdir "$out"
    cp -rf ${./.}/* "$out"
    mkdir "$out/.idx"
    cp -rf ${./.}/${environment}/.idx "$out"
    chmod -R u+w "$out"
  '';
}