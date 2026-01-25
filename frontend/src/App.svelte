<script>
  export let printerName = 'Kobra';
  const actions = [
    { title: 'Refresh Apps', description: 'Reload the installed Rinkhals apps.' },
    { title: 'ACE Status', description: 'Inspect the ACE drying cabinet state.' },
    { title: 'Firmware Update', description: 'Check LAN/cloud update availability.' }
  ];
</script>

<main>
  <section class="hero">
    <p class="eyebrow">Rinkhals Control</p>
    <h1>Manage your {printerName} from the browser.</h1>
    <p class="lede">
      This Svelte-driven interface is just a placeholder so you can iterate on the UI.
    </p>
    <div class="cta">
      <a class="button" href="#getting-started">Explore Actions</a>
      <a class="ghost" href="https://github.com/basvd/Rinkhals.WebUI" target="_blank" rel="noreferrer">Project Source</a>
    </div>
  </section>

  <section id="getting-started" class="panel">
    <h2>Next Steps</h2>
    <ul>
      {#each actions as action}
        <li>
          <h3>{action.title}</h3>
          <p>{action.description}</p>
        </li>
      {/each}
    </ul>
  </section>
</main>
