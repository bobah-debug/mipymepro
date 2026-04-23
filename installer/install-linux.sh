#!/bin/bash
set -e

echo "======================================"
echo "  Sistema PyME Chile - Instalación"
echo "======================================"

if ! command -v docker &> /dev/null; then
    echo "Docker no encontrado. Instalando..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    echo "Docker instalado. Es necesario reiniciar sesión."
fi

if ! command -v docker compose &> /dev/null; then
    echo "Instalando Docker Compose..."
    sudo apt-get install -y docker-compose-plugin 2>/dev/null || \
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose && sudo chmod +x /usr/local/bin/docker-compose
fi

INSTALL_DIR="$HOME/pyme-chile"
mkdir -p "$INSTALL_DIR"
cp -r . "$INSTALL_DIR/"

cat > "$INSTALL_DIR/start.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
docker compose up -d
echo "Sistema iniciado. Accede en: http://localhost"
xdg-open http://localhost 2>/dev/null || open http://localhost 2>/dev/null || true
EOF
chmod +x "$INSTALL_DIR/start.sh"

cat > "$INSTALL_DIR/stop.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
docker compose down
echo "Sistema detenido."
EOF
chmod +x "$INSTALL_DIR/stop.sh"

cat > "$HOME/Desktop/PyME-Chile.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Sistema PyME Chile
Comment=Sistema de Administración Empresarial
Exec=$INSTALL_DIR/start.sh
Icon=applications-office
Terminal=false
Categories=Office;
EOF
chmod +x "$HOME/Desktop/PyME-Chile.desktop"

cd "$INSTALL_DIR"
echo "Construyendo sistema..."
docker compose build

echo ""
echo "======================================"
echo "Instalación completada!"
echo ""
echo "Para iniciar el sistema:"
echo "  $INSTALL_DIR/start.sh"
echo ""
echo "O haz doble clic en 'PyME-Chile' del escritorio"
echo ""
echo "URL: http://localhost"
echo "Usuario: admin"
echo "Contraseña: admin1234"
echo "======================================"
