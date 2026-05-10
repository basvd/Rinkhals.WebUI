<script>
  import IconLight from '@material-symbols/svg-400/rounded/light_mode-fill.svg?component';
  import IconDark from '@material-symbols/svg-400/rounded/dark_mode-fill.svg?component';
  import IconSystem from '@material-symbols/svg-400/rounded/monitor.svg?component';

  /** @type {'system' | 'light' | 'dark'} */
  let theme = $state(
    /** @type {'system' | 'light' | 'dark'} */
    (localStorage.getItem('theme') || 'system')
  );

  function applyTheme(/** @type {'system' | 'light' | 'dark'} */ t) {
    theme = t;
    if (t === 'dark' || t === 'light') {
      document.documentElement.setAttribute('data-theme', t);
      localStorage.setItem('theme', t);
    } else {
      localStorage.removeItem('theme');
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
    }
  }
</script>

<div role="tablist" class="tabs tabs-box tabs-sm mx-2 flex-nowrap">
  <button
    role="tab"
    title="System theme"
    class="tab {theme === 'system' ? 'tab-active' : ''}"
    onclick={() => applyTheme('system')}
  >
    <IconSystem class="icon-inline" />
  </button>
  <button
    role="tab"
    title="Light theme"
    class="tab {theme === 'light' ? 'tab-active' : ''}"
    onclick={() => applyTheme('light')}
  >
    <IconLight class="icon-inline" />
  </button>
  <button
    role="tab"
    title="Dark theme"
    class="tab {theme === 'dark' ? 'tab-active' : ''}"
    onclick={() => applyTheme('dark')}
  >
    <IconDark class="icon-inline" />
  </button>
</div>
