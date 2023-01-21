<script lang="ts">
  import "@picocss/pico/css/pico.min.css";

  export let data: any;
  $: client_status = data && data.client_status;
  $: console.log(client_status);
</script>

<main class="container">
  <nav class="box">
    <div>
      <a href="/">[ home ]</a>
      <a href="https://github.com/dsgt-birdclef/birdclef-2023">[ github ]</a>
    </div>
    {#if client_status}
      <div>
        <b>app</b>: v{client_status.version}
        <b>build time</b>: {client_status.build_time}
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
