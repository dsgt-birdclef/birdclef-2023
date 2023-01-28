<script lang="ts">
  import "sakura.css/css/sakura.css";
  import { DateTime } from "luxon";

  export let data: any;
  let github_url = "https://github.com/dsgt-birdclef/birdclef-2023";
  $: client_status = data && data.client_status;
  $: build_time = client_status && DateTime.fromISO(client_status.build_time);
</script>

<main class="container">
  <nav class="box">
    <div>
      <a href="/">[ home ]</a>
      <a href={github_url}>[ github ]</a>
    </div>
    {#if client_status}
      <div>
        <b>app</b>:
        <a href="{github_url}/commit/{client_status.commit_sha}">v{client_status.version}</a>
        <b>build time</b>: {build_time.toLocaleString(DateTime.DATETIME_MED)}
      </div>
    {/if}
  </nav>
  <slot />
</main>

<style>
  a {
    text-decoration: none;
  }
  .box {
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap-reverse;
  }
</style>
