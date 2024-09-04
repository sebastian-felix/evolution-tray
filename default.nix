{
  lib,
  fetchFromGitHub,
  python3,
  python3Packages,
  pkgs,
  gtk3,
  wrapGAppsHook,
  gtksourceview3,
  evolution,
  gobject-introspection,
}:
python3Packages.buildPythonApplication {
  pname = "evolution-tray";
  version = "0.1";

  src = "./";

  nativeBuildInputs = [wrapGAppsHook gobject-introspection];

  buildInputs = [
    python3
    pkgs.libwnck
    pkgs.libappindicator-gtk3
    pkgs.gsound
    pkgs.adwaita-icon-theme
    pkgs.evolution
  ];

  doCheck = false; # it doesn't have any tests

  propagatedBuildInputs = with python3Packages; [
    gtk3
    dbus-python
    pygobject3
    imapclient
    setuptools
    pyroute2
    secretstorage
    gtksourceview3
  ];

  meta = with lib; {
    description = "Tray for Evolution mail client";
    longDescription = ''
      This is a tray for the Evolution mail client. It allows you to minimize
      Evolution to the tray and still receive notifications.'';
    homepage = "https://github.com/sebastian-felix/evolution-tray";
    license = licenses.gpl2Plus;
    platforms = platforms.linux;
    maintainers = with maintainers; [sebastian-felix];
    mainProgram = "evolution-tray";
  };
}
