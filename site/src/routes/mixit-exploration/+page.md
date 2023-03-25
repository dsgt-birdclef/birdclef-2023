<script>
    import Explorer from "./Explorer.svelte";
    export let data;
    import { ssp, queryParam } from "sveltekit-search-params";
    $: options = {autoColumns:true, pagination: "local", paginationSize: 4};
    let detailed_view = queryParam("detailed", ssp.boolean(false));
    let track_name = queryParam("track", {defaultValue: data.subset[0].filename});
</script>

# mixit exploration

You can explore the results of running mixit on a small subset of 30 second training examples from the 2023 dataset.

## options

<!-- add audio tracks for the original and source0 to source3 -->
<div style="border: 1px solid black">
  <!-- drop down with track names -->
  <label>
    track name:
    <select bind:value={$track_name}>
      {#each data.subset as track}
        <option value={track.filename}>{track.filename}</option>
      {/each}
    </select>
  </label>
  <!-- checkbox for option -->
  <label>
    detailed viewed:
    <input type="checkbox" bind:checked={$detailed_view} />
  </label>
</div>

<Explorer track_name={$track_name} detailed_view={$detailed_view} />
