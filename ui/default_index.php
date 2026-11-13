<?php
/* aetherstack-default-index */
// Escanear el directorio actual para encontrar subcarpetas
$all_files = scandir(__DIR__);
$projects = [];

// Paleta alegre de avatares según inicial o índice
$avatar_gradients = [
    ['from' => '#3b82f6', 'to' => '#06b6d4'], // Cyan / Blue
    ['from' => '#8b5cf6', 'to' => '#ec4899'], // Violet / Pink
    ['from' => '#f97316', 'to' => '#facc15'], // Orange / Amber
    ['from' => '#10b981', 'to' => '#14b8a6'], // Emerald / Teal
    ['from' => '#6366f1', 'to' => '#a855f7'], // Indigo / Purple
    ['from' => '#ef4444', 'to' => '#f97316'], // Red / Orange
    ['from' => '#06b6d4', 'to' => '#3b82f6'], // Teal / Blue
    ['from' => '#ec4899', 'to' => '#f43f5e'], // Pink / Rose
];

// Detectar tipo de proyecto con estilos alegres
function detectProjectType(string $dir): array {
    $path = __DIR__ . '/' . $dir;
    if (file_exists($path . '/wp-config.php')) {
        return ['name' => 'WordPress', 'key' => 'wp',      'bg' => '#eff6ff', 'text' => '#1d4ed8', 'border' => '#bfdbfe'];
    }
    if (file_exists($path . '/artisan')) {
        return ['name' => 'Laravel',   'key' => 'laravel', 'bg' => '#fff1f2', 'text' => '#be123c', 'border' => '#fecdd3'];
    }
    if (file_exists($path . '/next.config.js') || file_exists($path . '/next.config.ts') || file_exists($path . '/next.config.mjs')) {
        return ['name' => 'Next.js',   'key' => 'next',    'bg' => '#f8fafc', 'text' => '#0f172a', 'border' => '#cbd5e1'];
    }
    if (file_exists($path . '/nuxt.config.ts') || file_exists($path . '/nuxt.config.js')) {
        return ['name' => 'Nuxt.js',   'key' => 'nuxt',    'bg' => '#ecfdf5', 'text' => '#047857', 'border' => '#a7f3d0'];
    }
    if (file_exists($path . '/vite.config.js') || file_exists($path . '/vite.config.ts')) {
        return ['name' => 'Vite',      'key' => 'vite',    'bg' => '#f5f3ff', 'text' => '#6d28d9', 'border' => '#ddd6fe'];
    }
    if (file_exists($path . '/package.json')) {
        return ['name' => 'Node.js',   'key' => 'node',    'bg' => '#f0fdf4', 'text' => '#15803d', 'border' => '#bbf7d0'];
    }
    if (file_exists($path . '/index.html')) {
        return ['name' => 'HTML5',     'key' => 'html',    'bg' => '#fff7ed', 'text' => '#c2410c', 'border' => '#fed7aa'];
    }
    if (file_exists($path . '/composer.json')) {
        return ['name' => 'PHP',       'key' => 'php',     'bg' => '#eef2ff', 'text' => '#4338ca', 'border' => '#c7d2fe'];
    }
    return ['name' => 'Project',       'key' => 'folder',  'bg' => '#f1f5f9', 'text' => '#475569', 'border' => '#e2e8f0'];
}

$index = 0;
foreach ($all_files as $file) {
    if ($file !== '.' && $file !== '..' && is_dir(__DIR__ . '/' . $file) && strpos($file, '.') !== 0) {
        $type = detectProjectType($file);
        $hasWpAdmin = file_exists(__DIR__ . '/' . $file . '/wp-admin');
        $grad = $avatar_gradients[$index % count($avatar_gradients)];
        $projects[] = [
            'name'       => $file,
            'type'       => $type['name'],
            'typeKey'    => $type['key'],
            'typeBg'     => $type['bg'],
            'typeText'   => $type['text'],
            'typeBorder' => $type['border'],
            'hasWpAdmin' => $hasWpAdmin,
            'initial'    => mb_strtoupper(mb_substr($file, 0, 1)),
            'gradFrom'   => $grad['from'],
            'gradTo'     => $grad['to'],
        ];
        $index++;
    }
}

$total = count($projects);
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Workspace · <?php echo $total; ?> <?php echo $total === 1 ? 'project' : 'projects'; ?></title>
    <script>
        (function() {
            try {
                var stored = localStorage.getItem('workspace_theme');
                var prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                var theme = stored || (prefersDark ? 'dark' : 'light');
                document.documentElement.setAttribute('data-theme', theme);
            } catch (e) {}
        })();
    </script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            /* Paleta clara, alegre y sólida (sin glassmorphism) */
            --bg-canvas:       #f8fafc;
            --surface-table:   #ffffff;
            --surface-subtle:  #f1f5f9;
            --surface-hover:   #f8faff;
            --border-light:    #e2e8f0;
            --border-subtle:   #f1f5f9;
            
            --text-main:       #0f172a;
            --text-muted:      #64748b;
            --text-faint:      #94a3b8;
            
            --brand-primary:   #4f46e5;
            --brand-primary-h: #4338ca;
            --brand-green:     #10b981;
            
            --shadow-subtle:   0 1px 3px rgba(15, 23, 42, 0.05);
            --shadow-table:    0 4px 16px -2px rgba(15, 23, 42, 0.06), 0 2px 6px -1px rgba(15, 23, 42, 0.04);
            --shadow-focus:    0 0 0 4px rgba(99, 102, 241, 0.16);

            --thead-bg:        #fcfdfe;
            --badge-count-bg:  #eef2ff;
            --badge-count-text:#4338ca;
            --badge-count-border:#c7d2fe;
            --admin-btn-bg:    #eff6ff;
            --admin-btn-text:  #1d4ed8;
            --admin-btn-border:#bfdbfe;
            --admin-btn-hover: #dbeafe;
            
            --radius-box:      18px;
            --radius-btn:      10px;
            --radius-pill:     9999px;
            
            --transition-fast: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        }

        [data-theme="dark"] {
            --bg-canvas:       #0b0f19;
            --surface-table:   #111827;
            --surface-subtle:  #1f2937;
            --surface-hover:   #1e293b;
            --border-light:    #1f2937;
            --border-subtle:   #1e293b;

            --text-main:       #f8fafc;
            --text-muted:      #94a3b8;
            --text-faint:      #64748b;

            --brand-primary:   #6366f1;
            --brand-primary-h: #4f46e5;
            --brand-green:     #10b981;

            --shadow-subtle:   0 1px 3px rgba(0, 0, 0, 0.3);
            --shadow-table:    0 8px 24px -4px rgba(0, 0, 0, 0.45);
            --shadow-focus:    0 0 0 4px rgba(99, 102, 241, 0.3);

            --thead-bg:        #141d2e;
            --badge-count-bg:  #1e1b4b;
            --badge-count-text:#a5b4fc;
            --badge-count-border:#3730a3;
            --admin-btn-bg:    #172554;
            --admin-btn-text:  #93c5fd;
            --admin-btn-border:#1e3a8a;
            --admin-btn-hover: #1e40af;
        }

        *, *::before, *::after {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
            background-color: var(--bg-canvas);
            background-image:
                radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.07) 0px, transparent 50%),
                radial-gradient(at 100% 0%, rgba(244, 63, 94, 0.06) 0px, transparent 45%);
            background-attachment: fixed;
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 2.5rem 1.5rem 2rem;
            -webkit-font-smoothing: antialiased;
            transition: background-color 0.25s ease, color 0.25s ease;
        }

        [data-theme="dark"] body {
            background-image:
                radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.12) 0px, transparent 50%),
                radial-gradient(at 100% 0%, rgba(244, 63, 94, 0.1) 0px, transparent 45%);
        }

        /* ─── HEADER ─── */
        header {
            width: 100%;
            max-width: 1120px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 2rem;
            gap: 1.25rem;
            flex-wrap: wrap;
        }

        .header-brand {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .header-logo-badge {
            width: 48px;
            height: 48px;
            border-radius: 14px;
            background: linear-gradient(135deg, #4f46e5 0%, #ec4899 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #ffffff;
            box-shadow: 0 8px 16px -2px rgba(79, 70, 229, 0.3);
            flex-shrink: 0;
        }

        .header-titles h1 {
            font-size: 1.75rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            color: var(--text-main);
            line-height: 1.15;
        }

        .header-titles h1 .title-gradient {
            background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .header-titles p {
            font-size: 0.88rem;
            color: var(--text-muted);
            font-weight: 500;
            margin-top: 0.2rem;
        }

        .header-status {
            display: flex;
            align-items: center;
            gap: 0.85rem;
            background: var(--surface-table);
            padding: 0.45rem 1rem;
            border-radius: var(--radius-pill);
            border: 1px solid var(--border-light);
            box-shadow: var(--shadow-subtle);
        }

        .status-indicator {
            display: flex;
            align-items: center;
            gap: 0.45rem;
            font-size: 0.8rem;
            font-weight: 700;
            color: #047857;
        }

        .status-dot {
            width: 9px;
            height: 9px;
            border-radius: 50%;
            background-color: var(--brand-green);
            box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.25);
            animation: pulse-dot 2.2s infinite;
        }

        @keyframes pulse-dot {
            0%, 100% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.15); opacity: 0.75; }
        }

        .badge-count {
            background: var(--badge-count-bg);
            color: var(--badge-count-text);
            padding: 0.25rem 0.75rem;
            border-radius: var(--radius-pill);
            font-size: 0.8rem;
            font-weight: 700;
            border: 1px solid var(--badge-count-border);
        }

        /* ─── THEME TOGGLE ─── */
        .btn-theme-toggle {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 36px;
            height: 36px;
            border-radius: var(--radius-pill);
            background: var(--surface-subtle);
            border: 1px solid var(--border-light);
            color: var(--text-main);
            cursor: pointer;
            transition: var(--transition-fast);
        }

        .btn-theme-toggle:hover {
            background: var(--surface-hover);
            border-color: var(--brand-primary);
            color: var(--brand-primary);
            transform: scale(1.05);
        }

        .btn-lang-toggle {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            height: 36px;
            padding: 0 0.7rem;
            border-radius: var(--radius-pill);
            background: var(--surface-subtle);
            border: 1px solid var(--border-light);
            color: var(--text-main);
            font-family: inherit;
            font-size: 0.75rem;
            font-weight: 800;
            letter-spacing: 0.04em;
            cursor: pointer;
            transition: var(--transition-fast);
        }

        .btn-lang-toggle:hover {
            background: var(--surface-hover);
            border-color: var(--brand-primary);
            color: var(--brand-primary);
            transform: scale(1.05);
        }

        .btn-theme-toggle svg {
            transition: transform 0.2s ease;
        }

        .icon-sun { display: none; }
        .icon-moon { display: block; }

        [data-theme="dark"] .icon-sun { display: block; }
        [data-theme="dark"] .icon-moon { display: none; }

        /* ─── CONTROLES (SEARCH + STATS) ─── */
        .controls-bar {
            width: 100%;
            max-width: 1120px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1.25rem;
            gap: 1rem;
            flex-wrap: wrap;
        }

        .search-box {
            position: relative;
            display: flex;
            align-items: center;
            background: var(--surface-table);
            border: 2px solid var(--border-light);
            border-radius: var(--radius-pill);
            padding: 0.35rem 0.6rem 0.35rem 1rem;
            box-shadow: var(--shadow-subtle);
            width: 100%;
            max-width: 440px;
            transition: var(--transition-fast);
        }

        .search-box:focus-within {
            border-color: var(--brand-primary);
            box-shadow: var(--shadow-focus);
        }

        .search-icon {
            color: var(--text-faint);
            display: flex;
            margin-right: 0.65rem;
            flex-shrink: 0;
        }

        .search-box:focus-within .search-icon {
            color: var(--brand-primary);
        }

        .search-input {
            width: 100%;
            border: none;
            outline: none;
            font-family: inherit;
            font-size: 0.92rem;
            font-weight: 500;
            color: var(--text-main);
            background: transparent;
        }

        .search-input::placeholder {
            color: var(--text-faint);
            font-weight: 400;
        }

        .search-tools {
            display: flex;
            align-items: center;
            gap: 0.35rem;
        }

        .kbd-badge {
            background: var(--surface-subtle);
            border: 1px solid var(--border-light);
            color: var(--text-muted);
            border-radius: 6px;
            padding: 0.15rem 0.4rem;
            font-size: 0.7rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 2px;
        }

        .clear-btn {
            background: transparent;
            border: none;
            color: var(--text-muted);
            cursor: pointer;
            width: 28px;
            height: 28px;
            border-radius: 50%;
            display: none;
            align-items: center;
            justify-content: center;
            transition: var(--transition-fast);
        }

        .clear-btn:hover {
            background: #fee2e2;
            color: #ef4444;
        }

        .result-stats {
            font-size: 0.88rem;
            color: var(--text-muted);
            font-weight: 600;
        }

        .result-stats strong {
            color: var(--text-main);
            font-weight: 800;
        }

        /* ─── TABLA DE PROYECTOS ─── */
        .table-container {
            width: 100%;
            max-width: 1120px;
            background: var(--surface-table);
            border-radius: var(--radius-box);
            border: 1px solid var(--border-light);
            box-shadow: var(--shadow-table);
            overflow: hidden;
        }

        .projects-table {
            width: 100%;
            border-collapse: collapse;
            text-align: left;
        }

        .projects-table thead {
            background: var(--thead-bg);
            border-bottom: 2px solid var(--border-light);
        }

        .projects-table th {
            padding: 1rem 1.25rem;
            font-size: 0.78rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            user-select: none;
        }

        .th-sortable {
            cursor: pointer;
            transition: color 0.15s ease;
        }

        .th-sortable:hover {
            color: var(--brand-primary);
        }

        .th-sortable .sort-arrow {
            display: inline-block;
            margin-left: 0.3rem;
            opacity: 0.4;
            font-size: 0.85rem;
        }

        .th-sortable.active .sort-arrow {
            opacity: 1;
            color: var(--brand-primary);
        }

        /* Filas de la tabla */
        .project-row {
            border-bottom: 1px solid var(--border-subtle);
            transition: background-color 0.18s ease;
        }

        .project-row:last-child {
            border-bottom: none;
        }

        .project-row:hover {
            background-color: var(--surface-hover);
        }

        .projects-table td {
            padding: 1rem 1.25rem;
            vertical-align: middle;
            font-size: 0.92rem;
        }

        /* Columna 1: Proyecto con Avatar */
        .project-cell {
            display: flex;
            align-items: center;
            gap: 0.9rem;
        }

        .project-avatar {
            width: 38px;
            height: 38px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #ffffff;
            font-size: 1.1rem;
            font-weight: 800;
            flex-shrink: 0;
            box-shadow: 0 3px 8px rgba(0, 0, 0, 0.12);
        }

        .project-name-text {
            font-weight: 800;
            color: var(--text-main);
            letter-spacing: -0.015em;
        }

        /* Columna 2: Tecnología Badge */
        .tech-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            padding: 0.28rem 0.75rem;
            border-radius: var(--radius-pill);
            font-size: 0.75rem;
            font-weight: 700;
            border: 1px solid;
            letter-spacing: 0.02em;
        }

        .tech-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background-color: currentColor;
        }

        /* Columna 3: URL virtual + copiar */
        .url-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            font-size: 0.82rem;
            font-weight: 600;
            color: var(--text-muted);
            background: var(--surface-subtle);
            padding: 0.35rem 0.65rem;
            border-radius: 8px;
            cursor: pointer;
            border: 1px solid transparent;
            transition: var(--transition-fast);
            position: relative;
        }

        .url-pill:hover {
            color: var(--brand-primary);
            background: var(--surface-subtle);
            border-color: var(--brand-primary);
        }

        .copy-tooltip {
            position: absolute;
            left: 50%;
            bottom: calc(100% + 6px);
            transform: translateX(-50%);
            background: #0f172a;
            color: #ffffff;
            font-size: 0.7rem;
            font-weight: 700;
            padding: 0.25rem 0.6rem;
            border-radius: 6px;
            white-space: nowrap;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.15s ease;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
            z-index: 20;
        }

        .copy-tooltip::after {
            content: '';
            position: absolute;
            top: 100%;
            left: 50%;
            transform: translateX(-50%);
            border: 4px solid transparent;
            border-top-color: #0f172a;
        }

        .url-pill.copied .copy-tooltip {
            opacity: 1;
        }

        /* Columna 4: Acciones */
        .actions-cell {
            display: flex;
            align-items: center;
            justify-content: flex-end;
            gap: 0.5rem;
        }

        .btn-action-launch {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            background: var(--brand-primary);
            color: #ffffff;
            text-decoration: none;
            padding: 0.45rem 0.85rem;
            border-radius: var(--radius-btn);
            font-size: 0.82rem;
            font-weight: 700;
            box-shadow: 0 2px 6px rgba(79, 70, 229, 0.25);
            transition: var(--transition-fast);
            border: none;
        }

        .btn-action-launch:hover {
            background: var(--brand-primary-h);
            transform: translateY(-1px);
            box-shadow: 0 4px 10px rgba(79, 70, 229, 0.35);
            color: #ffffff;
        }

        .btn-action-admin {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            background: var(--admin-btn-bg);
            color: var(--admin-btn-text);
            border: 1px solid var(--admin-btn-border);
            text-decoration: none;
            padding: 0.45rem 0.75rem;
            border-radius: var(--radius-btn);
            font-size: 0.82rem;
            font-weight: 700;
            transition: var(--transition-fast);
        }

        .btn-action-admin:hover {
            background: var(--admin-btn-hover);
            color: var(--admin-btn-text);
            transform: translateY(-1px);
        }

        /* Estado Vacío */
        .empty-row td {
            text-align: center;
            padding: 4rem 1.5rem;
        }

        .empty-box {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 0.5rem;
        }

        .empty-icon {
            width: 52px;
            height: 52px;
            background: #fee2e2;
            color: #ef4444;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 0.5rem;
        }

        .empty-box h3 {
            font-size: 1.15rem;
            font-weight: 800;
            color: var(--text-main);
        }

        .empty-box p {
            color: var(--text-muted);
            font-size: 0.9rem;
        }

        /* ─── FOOTER ─── */
        footer {
            margin-top: 3rem;
            display: flex;
            align-items: center;
            gap: 0.85rem;
            color: var(--text-muted);
            font-size: 0.82rem;
            font-weight: 600;
            background: var(--surface-table);
            padding: 0.5rem 1.2rem;
            border-radius: var(--radius-pill);
            border: 1px solid var(--border-light);
            box-shadow: var(--shadow-subtle);
        }

        .clock-badge {
            display: flex;
            align-items: center;
            gap: 0.4rem;
            color: var(--text-main);
            font-weight: 700;
            font-variant-numeric: tabular-nums;
        }

        /* Responsive */
        @media (max-width: 768px) {
            body { padding: 1.5rem 1rem; }
            .projects-table th:nth-child(2),
            .projects-table td:nth-child(2) {
                display: none; /* Ocultar tecnología en pantallas muy estrechas */
            }
            .controls-bar { flex-direction: column; align-items: stretch; }
            .search-box { max-width: 100%; }
        }
    </style>
</head>
<body>

    <!-- Header Principal -->
    <header>
        <div class="header-brand">
            <div class="header-logo-badge">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <polygon points="12 2 2 7 12 12 22 7 12 2"/>
                    <polyline points="2 17 12 22 22 17"/>
                    <polyline points="2 12 12 17 22 12"/>
                </svg>
            </div>
            <div class="header-titles">
                <h1 id="header-title">My <span class="title-gradient">Projects</span></h1>
                <p id="header-subtitle">Local Workspace &bull; Active projects list</p>
            </div>
        </div>

        <div class="header-status">
            <div class="status-indicator">
                <span class="status-dot"></span>
                <span id="status-label">Local Server</span>
            </div>
            <span class="badge-count" id="visible-count"><?php echo $total; ?> <?php echo $total === 1 ? 'project' : 'projects'; ?></span>
            <button class="btn-lang-toggle" id="lang-toggle" title="Switch language (EN/ES)" aria-label="Switch language">EN</button>
            <button class="btn-theme-toggle" id="theme-toggle" title="Toggle theme (Light/Dark)" aria-label="Toggle theme">
                <svg class="icon-sun" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="5"/>
                    <line x1="12" y1="1" x2="12" y2="3"/>
                    <line x1="12" y1="21" x2="12" y2="23"/>
                    <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
                    <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
                    <line x1="1" y1="12" x2="3" y2="12"/>
                    <line x1="21" y1="12" x2="23" y2="12"/>
                    <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
                    <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
                </svg>
                <svg class="icon-moon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
                </svg>
            </button>
        </div>
    </header>

    <!-- Barra de búsqueda y contador -->
    <div class="controls-bar">
        <div class="search-box">
            <span class="search-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="11" cy="11" r="8"/>
                    <path d="m21 21-4.35-4.35"/>
                </svg>
            </span>
            <input type="text" id="search" class="search-input" placeholder="Search by name or technology..." autocomplete="off" spellcheck="false">
            <div class="search-tools">
                <div class="kbd-badge" id="search-kbd">
                    <span>Ctrl</span> + <span>K</span>
                </div>
                <button class="clear-btn" id="search-clear" title="Clear search" aria-label="Clear search">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
                        <path d="M18 6 6 18M6 6l12 12"/>
                    </svg>
                </button>
            </div>
        </div>

        <p class="result-stats" id="result-stats">
            Showing <strong id="count-label"><?php echo $total; ?></strong> of <?php echo $total; ?> projects
        </p>
    </div>

    <!-- Contenedor con Tabla de Proyectos -->
    <div class="table-container">
        <table class="projects-table">
            <thead>
                <tr>
                    <th class="th-sortable active" data-sort="name">
                        <span data-i18n="col_project">Project</span> <span class="sort-arrow">&uarr;</span>
                    </th>
                    <th class="th-sortable" data-sort="type">
                        <span data-i18n="col_tech">Technology</span> <span class="sort-arrow">&varr;</span>
                    </th>
                    <th data-i18n="col_link">Virtual Link</th>
                    <th style="text-align: right;" data-i18n="col_actions">Actions</th>
                </tr>
            </thead>
            <tbody id="projects-tbody">
                <?php foreach ($projects as $p): ?>
                    <?php
                        $url      = "http://" . htmlspecialchars($p['name']) . ".test";
                        $adminUrl = $url . "/wp-admin";
                    ?>
                    <tr class="project-row"
                        data-name="<?php echo strtolower(htmlspecialchars($p['name'])); ?>"
                        data-type="<?php echo htmlspecialchars($p['typeKey']); ?>">
                        
                        <!-- Columna: Proyecto -->
                        <td>
                            <div class="project-cell">
                                <div class="project-avatar" style="background: linear-gradient(135deg, <?php echo $p['gradFrom']; ?>, <?php echo $p['gradTo']; ?>);">
                                    <?php echo htmlspecialchars($p['initial']); ?>
                                </div>
                                <span class="project-name-text"><?php echo htmlspecialchars($p['name']); ?></span>
                            </div>
                        </td>

                        <!-- Columna: Tecnología -->
                        <td>
                            <span class="tech-badge"
                                  style="background-color: <?php echo $p['typeBg']; ?>; color: <?php echo $p['typeText']; ?>; border-color: <?php echo $p['typeBorder']; ?>;">
                                <span class="tech-dot"></span>
                                <?php echo htmlspecialchars($p['type']); ?>
                            </span>
                        </td>

                        <!-- Columna: Enlace Virtual -->
                        <td>
                            <div class="url-pill" data-url="<?php echo $url; ?>" title="Click to copy link">
                                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
                                    <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
                                </svg>
                                <span><?php echo htmlspecialchars($p['name']); ?>.test</span>
                                <span class="copy-tooltip">Link copied!</span>
                            </div>
                        </td>

                        <!-- Columna: Acciones -->
                        <td>
                            <div class="actions-cell">
                                <a href="<?php echo $url; ?>" class="btn-action-launch" target="_blank" rel="noopener">
                                    <span data-i18n="open">Open</span>
                                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                                        <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                                        <polyline points="15 3 21 3 21 9"/>
                                        <line x1="10" y1="14" x2="21" y2="3"/>
                                    </svg>
                                </a>

                                <?php if ($p['hasWpAdmin']): ?>
                                <a href="<?php echo $adminUrl; ?>" class="btn-action-admin" target="_blank" rel="noopener" title="Go to WP Admin panel">
                                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                                        <circle cx="12" cy="12" r="10"/>
                                        <path d="M12 2a10 10 0 0 1 0 20"/>
                                        <path d="M2 12h20"/>
                                    </svg>
                                    <span>Admin</span>
                                </a>
                                <?php endif; ?>
                            </div>
                        </td>
                    </tr>
                <?php endforeach; ?>

                <!-- Fila vacía para cuando no haya coincidencias -->
                <tr class="empty-row" id="empty-row" style="display: none;">
                    <td colspan="4">
                        <div class="empty-box">
                            <div class="empty-icon">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                                    <circle cx="11" cy="11" r="8"/>
                                    <path d="m21 21-4.35-4.35"/>
                                </svg>
                            </div>
                            <h3 id="empty-title">No projects found</h3>
                            <p id="empty-subtitle">Try another term in the search bar.</p>
                        </div>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>

    <!-- Footer -->
    <footer>
        <div class="clock-badge">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 16 14"/>
            </svg>
            <span id="clock">--:--:--</span>
        </div>
        <span>&bull;</span>
        <span id="footer-env">Virtual Environments (*.test)</span>
    </footer>

    <!-- Lógica de Interactividad -->
    <script>
    (() => {
        /* Idioma EN / ES (por defecto EN) */
        const I18N = {
            en: {
                titleHtml: 'My <span class="title-gradient">Projects</span>',
                subtitle: 'Local Workspace &bull; Active projects list',
                status: 'Local Server',
                singular: 'project',
                plural: 'projects',
                searchPlaceholder: 'Search by name or technology...',
                clearTitle: 'Clear search',
                showing: 'Showing',
                of: 'of',
                col_project: 'Project',
                col_tech: 'Technology',
                col_link: 'Virtual Link',
                col_actions: 'Actions',
                copyTitle: 'Click to copy link',
                copied: 'Link copied!',
                open: 'Open',
                adminTitle: 'Go to WP Admin panel',
                emptyTitle: 'No projects found',
                emptySubtitle: 'Try another term in the search bar.',
                footerEnv: 'Virtual Environments (*.test)',
                themeTitle: 'Toggle theme (Light/Dark)',
                langTitle: 'Switch language (EN/ES)',
                folderType: 'Project',
                locale: 'en-US'
            },
            es: {
                titleHtml: 'Mis <span class="title-gradient">Proyectos</span>',
                subtitle: 'Local Workspace &bull; Lista de proyectos activos',
                status: 'Servidor Local',
                singular: 'proyecto',
                plural: 'proyectos',
                searchPlaceholder: 'Buscar por nombre o tecnología...',
                clearTitle: 'Limpiar búsqueda',
                showing: 'Mostrando',
                of: 'de',
                col_project: 'Proyecto',
                col_tech: 'Tecnología',
                col_link: 'Enlace Virtual',
                col_actions: 'Acciones',
                copyTitle: 'Click para copiar enlace',
                copied: '¡Enlace copiado!',
                open: 'Abrir',
                adminTitle: 'Ir al panel WP Admin',
                emptyTitle: 'No se encontraron proyectos',
                emptySubtitle: 'Intenta con otro término en la barra de búsqueda.',
                footerEnv: 'Entornos Virtuales (*.test)',
                themeTitle: 'Cambiar tema (Claro/Oscuro)',
                langTitle: 'Cambiar idioma (EN/ES)',
                folderType: 'Proyecto',
                locale: 'es-CO'
            }
        };

        let currentLang = localStorage.getItem('workspace_lang') || 'en';
        if (!I18N[currentLang]) currentLang = 'en';

        const totalProjects = <?php echo $total; ?>;
        const langToggle = document.getElementById('lang-toggle');
        const themeToggle = document.getElementById('theme-toggle');

        /* Buscador en tiempo real */
        const searchInput  = document.getElementById('search');
        const searchKbd    = document.getElementById('search-kbd');
        const searchClear  = document.getElementById('search-clear');
        const visibleCount = document.getElementById('visible-count');
        const resultStats  = document.getElementById('result-stats');
        const emptyRow     = document.getElementById('empty-row');
        const allRows      = [...document.querySelectorAll('.project-row')];
        let visibleMatches = totalProjects;

        function updateCounts() {
            const t = I18N[currentLang];
            const word = visibleMatches === 1 ? t.singular : t.plural;
            visibleCount.textContent = visibleMatches + ' ' + word;
            resultStats.innerHTML = `${t.showing} <strong id="count-label">${visibleMatches}</strong> ${t.of} ${totalProjects} ${totalProjects === 1 ? t.singular : t.plural}`;
            document.title = `Workspace · ${totalProjects} ${totalProjects === 1 ? t.singular : t.plural}`;
        }

        function applyLanguage(lang) {
            currentLang = lang;
            const t = I18N[lang];
            document.documentElement.setAttribute('lang', lang);
            localStorage.setItem('workspace_lang', lang);

            if (langToggle) {
                langToggle.textContent = lang.toUpperCase();
                langToggle.title = t.langTitle;
            }
            if (themeToggle) themeToggle.title = t.themeTitle;

            document.getElementById('header-title').innerHTML = t.titleHtml;
            document.getElementById('header-subtitle').innerHTML = t.subtitle;
            document.getElementById('status-label').textContent = t.status;
            searchInput.placeholder = t.searchPlaceholder;
            searchClear.title = t.clearTitle;
            document.getElementById('empty-title').textContent = t.emptyTitle;
            document.getElementById('empty-subtitle').textContent = t.emptySubtitle;
            document.getElementById('footer-env').textContent = t.footerEnv;

            document.querySelectorAll('[data-i18n]').forEach(el => {
                const key = el.getAttribute('data-i18n');
                if (t[key]) el.textContent = t[key];
            });
            document.querySelectorAll('.url-pill').forEach(p => { p.title = t.copyTitle; });
            document.querySelectorAll('.copy-tooltip').forEach(el => { el.textContent = t.copied; });
            document.querySelectorAll('.btn-action-admin').forEach(el => { el.title = t.adminTitle; });
            allRows.forEach(row => {
                if (row.dataset.type === 'folder') {
                    const badge = row.querySelector('.tech-badge');
                    if (badge && badge.lastChild) badge.lastChild.textContent = ' ' + t.folderType;
                }
            });

            updateCounts();
            updateClock();
        }

        if (langToggle) {
            langToggle.addEventListener('click', () => {
                applyLanguage(currentLang === 'en' ? 'es' : 'en');
            });
        }

        /* Tema Oscuro / Claro con persistencia */
        const storedTheme = localStorage.getItem('workspace_theme');
        const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        const currentTheme = storedTheme || (prefersDark ? 'dark' : 'light');

        document.documentElement.setAttribute('data-theme', currentTheme);

        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                const active = document.documentElement.getAttribute('data-theme');
                const next = active === 'dark' ? 'light' : 'dark';
                document.documentElement.setAttribute('data-theme', next);
                localStorage.setItem('workspace_theme', next);
            });
        }

        /* Reloj en vivo */
        const clockEl = document.getElementById('clock');
        function updateClock() {
            clockEl.textContent = new Date().toLocaleTimeString(I18N[currentLang].locale, {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
        }

        applyLanguage(currentLang);
        setInterval(updateClock, 1000);

        function filterProjects(term) {
            const query = term.toLowerCase().trim();
            let matches = 0;

            allRows.forEach(row => {
                const name = row.dataset.name || '';
                const type = row.dataset.type || '';
                const isMatch = name.includes(query) || type.includes(query);

                row.style.display = isMatch ? '' : 'none';
                if (isMatch) matches++;
            });

            visibleMatches = matches;
            updateCounts();
            emptyRow.style.display = matches === 0 ? '' : 'none';

            searchClear.style.display = query ? 'flex' : 'none';
            searchKbd.style.display   = query ? 'none' : 'flex';
        }

        searchInput.addEventListener('input', e => filterProjects(e.target.value));

        searchClear.addEventListener('click', () => {
            searchInput.value = '';
            filterProjects('');
            searchInput.focus();
        });

        /* Atajo de teclado Ctrl+K / Cmd+K */
        document.addEventListener('keydown', e => {
            if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
                e.preventDefault();
                searchInput.focus();
                searchInput.select();
            }
            if (e.key === 'Escape' && document.activeElement === searchInput) {
                searchInput.blur();
            }
        });

        /* Ordenación por columnas de la tabla */
        const sortHeaders = document.querySelectorAll('.th-sortable');
        const tbody = document.getElementById('projects-tbody');
        let currentSort = 'name';
        let sortAsc = true;

        sortHeaders.forEach(th => {
            th.addEventListener('click', () => {
                const sortKey = th.dataset.sort;

                if (currentSort === sortKey) {
                    sortAsc = !sortAsc;
                } else {
                    currentSort = sortKey;
                    sortAsc = true;
                }

                sortHeaders.forEach(h => {
                    h.classList.remove('active');
                    h.querySelector('.sort-arrow').innerHTML = '&varr;';
                });

                th.classList.add('active');
                th.querySelector('.sort-arrow').innerHTML = sortAsc ? '&uarr;' : '&darr;';

                const rows = [...document.querySelectorAll('.project-row')];
                rows.sort((a, b) => {
                    const valA = a.dataset[sortKey] || '';
                    const valB = b.dataset[sortKey] || '';
                    return sortAsc ? valA.localeCompare(valB) : valB.localeCompare(valA);
                });

                rows.forEach(r => tbody.insertBefore(r, emptyRow));
            });
        });

        /* Copiar enlace al portapapeles */
        document.querySelectorAll('.url-pill').forEach(pill => {
            pill.addEventListener('click', async (e) => {
                e.preventDefault();
                e.stopPropagation();
                const url = pill.dataset.url;
                try {
                    await navigator.clipboard.writeText(url);
                    pill.classList.add('copied');
                    setTimeout(() => pill.classList.remove('copied'), 1600);
                } catch {
                    const temp = document.createElement('input');
                    temp.value = url;
                    document.body.appendChild(temp);
                    temp.select();
                    document.execCommand('copy');
                    document.body.removeChild(temp);
                    pill.classList.add('copied');
                    setTimeout(() => pill.classList.remove('copied'), 1600);
                }
            });
        });
    })();
    </script>
</body>
</html>
