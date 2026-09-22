# New-Year-Clock
# 🎄 New Year Widget

A festive New Year countdown widget for Linux.

![New Year Widget](https://img.shields.io/badge/Linux-Wayland-blue)
![Python](https://img.shields.io/badge/Python-3-green)
![GTK](https://img.shields.io/badge/GTK-3-orange)

## ✨ Features

* 🎄 Countdown to New Year
* ❄️ Animated snow
* 💡 Animated Christmas lights
* 🎅 Christmas decorations
* 📅 Calendar countdown mode
* ⏳ Total-days countdown mode
* 🖱️ Move the widget with the mouse
* 💾 Saves widget position
* 🔔 New Year sounds menu
* 🌙 Designed for Wayland
* 🖥️ GTK3 + GtkLayerShell

---

# 📦 Installation

## Arch Linux / Artix Linux

Install the required packages:

```bash
sudo pacman -S --needed \
    python \
    python-gobject \
    gtk3 \
    gtk-layer-shell \
    python-cairo \
    mpv \
    yt-dlp \
    git
```

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/new-year-widget.git
cd new-year-widget
```

Make the launcher executable:

```bash
chmod +x daemon new_year_widget
```

Install the commands:

```bash
sudo cp daemon /usr/local/bin/daemon
sudo cp new_year_widget /usr/local/bin/new_year_widget
```

---

# ▶️ Start

Start the widget:

```bash
daemon
```

Stop the widget:

```bash
daemon -kill
```

You can also start it directly:

```bash
python3 new-year-widget.py
```

---

# 🖱️ Widget controls

Right-click the widget to open the menu.

Available options:

* **Разрешить перемещать** — enables moving the widget
* **Режим: всего дней** — switches the countdown mode
* **🔔 Звуки НОВЫЙ ГОД!** — New Year sounds

When moving is enabled, drag the widget with the left mouse button.

The position is saved automatically.

---

# 🔔 New Year sounds

The widget can launch New Year music through `mpv`.

Right-click the widget and select:

**🔔 Звуки НОВЫЙ ГОД!**

The menu contains New Year music options.

> Music files themselves are not included in this repository.

---

# 🚀 Autostart

For Hyprland, add the following to your startup configuration:

```lua
hl.on("hyprland.start", function()
    hl.exec_cmd("daemon")
end)
```

Then reload Hyprland.

---

# 🐛 Troubleshooting

If the widget does not start, run:

```bash
python3 new-year-widget.py
```

This will show errors directly in the terminal.

Check that GTK Layer Shell is installed:

```bash
pacman -Qs gtk-layer-shell
```

Check that Python GTK works:

```bash
python3 -c "import gi; print('PyGObject OK')"
```

Check `mpv`:

```bash
mpv --version
```

---

# 📝 License

This project is released under the MIT License.
