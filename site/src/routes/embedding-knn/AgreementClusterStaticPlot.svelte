<script lang="ts">
  import { browser } from "$app/environment";

  export let data: any[] = [];
  let selected: string = "normoc";
  let api_url: string =
    "/api/v1/data/processed/birdclef-2022/birdnet-embeddings-with-neighbors-static/v1";

  $: names = data.map((d) => d["ego_primary_label"]);
</script>

<h5 style="display:inline">Species:</h5>
<select bind:value={selected}>
  {#each names as name}
    <option value={name}>{name}</option>
  {/each}
</select>

<h5>Distances</h5>
<img src="{api_url}/{selected}/distances.png" />
<h5>Ego Birdnet Label</h5>
<img src="{api_url}/{selected}/ego_birdnet_label.png" />
<h5>KNN Birdnet Label</h5>
<img src="{api_url}/{selected}/knn_birdnet_label.png" />

<style>
  label {
    display: inline-block;
    padding: 1px;
  }
  img {
    width: 100%;
  }
  .selection {
    outline: 1px solid black;
  }
</style>
