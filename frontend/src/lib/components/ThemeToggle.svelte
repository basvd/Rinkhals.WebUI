<script>
  import IconLight from '@material-symbols/svg-200/rounded/light_mode-fill.svg?component';
  import IconDark from '@material-symbols/svg-200/rounded/dark_mode-fill.svg?component';
  import IconSystem from '@material-symbols/svg-200/rounded/monitor-fill.svg?component';

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

<div class="join">
  <button
    type="button"
    title="System theme"
    class="btn btn-ghost btn-sm join-item {theme === 'system' ? 'btn-active' : ''}"
    onclick={() => applyTheme('system')}
  >
    <IconSystem width={16} height={16} fill="currentColor" />
  </button>
  <button
    type="button"
    title="Light theme"
    class="btn btn-ghost btn-sm join-item {theme === 'light' ? 'btn-active' : ''}"
    onclick={() => applyTheme('light')}
  >
    <IconLight width={16} height={16} fill="currentColor" />
  </button>
  <button
    type="button"
    title="Dark theme"
    class="btn btn-ghost btn-sm join-item {theme === 'dark' ? 'btn-active' : ''}"
    onclick={() => applyTheme('dark')}
  >
    <IconDark width={16} height={16} fill="currentColor" />
  </button>
</div>
