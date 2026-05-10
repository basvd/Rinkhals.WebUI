<script>
  import * as menu from '@zag-js/menu';
  import { portal, useMachine, normalizeProps } from '@zag-js/svelte';
  import ThemeToggle from './ThemeToggle.svelte';
  import IconControls from '@material-symbols/svg-400/rounded/tune-fill.svg?component';
  import IconApps from '@material-symbols/svg-400/rounded/apps-fill.svg?component';
  import IconSystem from '@material-symbols/svg-400/rounded/settings-fill.svg?component';
  import IconMenu from '@material-symbols/svg-400/rounded/menu.svg?component';

  const appVersion = __APP_VERSION__;

  /**
   * @type {{
   *   activeTab?: string,
   *   onTabChange?: (tab: string) => void,
   * }}
   */
  let { activeTab = 'controls', onTabChange } = $props();

  const TABS = [
    { id: 'controls', label: 'Controls', Icon: IconControls },
    { id: 'apps',     label: 'Apps',     Icon: IconApps },
    { id: 'system',   label: 'System',   Icon: IconSystem },
  ];

  const service = useMachine(menu.machine, {
    id: 'nav-menu',
    positioning: { placement: 'bottom-start' },
    onSelect(details) {
      onTabChange?.(details.value);
    },
  });
  const api = $derived(menu.connect(service, normalizeProps));
</script>

<div class="navbar shadow-sm shrink-0">
  <div class="navbar-start">
    <span class="flex items-center gap-2 px-2 text-xl whitespace-nowrap">
      <img src="/favicon.png" alt="Rinkhals" class="h-7 w-7" />
      Rinkhals WebUI
    </span>
    <div class="lg:hidden">
      <button {...api.getTriggerProps()} class="btn btn-ghost btn-sm btn-square text-xl">
        <IconMenu class="icon-inline" />
      </button>
      <div use:portal {...api.getPositionerProps()}>
        <ul {...api.getContentProps()} class="menu bg-base-200 rounded-box z-50 w-40 shadow-md outline-none">
          {#each TABS as tab (tab.id)}
            <li>
              <button
                {...api.getItemProps({ value: tab.id })}
                class={activeTab === tab.id ? 'active' : ''}
              >
                <tab.Icon class="icon-inline" />
                {tab.label}
              </button>
            </li>
          {/each}
        </ul>
      </div>
    </div>
  </div>
  <div class="navbar-center hidden lg:flex">
    <div role="tablist" class="tabs tabs-border">
      {#each TABS as tab (tab.id)}
        <button
          role="tab"
          class="tab gap-1.5 {activeTab === tab.id ? 'tab-active' : ''}"
          onclick={() => onTabChange?.(tab.id)}
        >
          <tab.Icon class="icon-inline" />
          {tab.label}
        </button>
      {/each}
    </div>
  </div>
  <div class="navbar-end gap-1">
    <a
      href="https://github.com/basvd/Rinkhals.WebUI"
      target="_blank"
      rel="noopener noreferrer"
      class="btn btn-ghost btn-sm btn-square"
      aria-label="GitHub repository"
    >
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 98 96" fill="currentColor" aria-hidden="true">
        <path d="M49 1a49 49 0 0 0-15.5 95.5c2.5.5 3.4-1 3.4-2.3v-8c-13.7 3-16.6-6.6-16.6-6.6-2.2-5.7-5.5-7.2-5.5-7.2-4.5-3 .3-3 .3-3 5 .3 7.6 5.1 7.6 5.1 4.4 7.6 11.6 5.4 14.4 4.1.4-3.2 1.7-5.4 3.1-6.6-11-1.2-22.5-5.5-22.5-24.4 0-5.4 1.9-9.8 5-13.2-.5-1.3-2.2-6.3.5-13 0 0 4.1-1.3 13.4 5a46.3 46.3 0 0 1 24.4 0c9.3-6.4 13.4-5 13.4-5 2.7 6.8 1 11.8.5 13 3.2 3.4 5 7.8 5 13.2 0 19-11.5 23.2-22.5 24.4 1.8 1.5 3.3 4.5 3.3 9.2v13.6c0 1.3.9 2.8 3.4 2.3A49 49 0 0 0 49 1z"/>
      </svg>
    </a>
    <span class="badge badge-soft badge-sm font-mono mr-5">{appVersion}</span>
    <!-- <div class="divider divider-horizontal"></div> -->
    <ThemeToggle />
  </div>
</div>
