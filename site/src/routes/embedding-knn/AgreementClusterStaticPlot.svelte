<script lang="ts">
    export let data: any[] = [];

    var names = data.map(d => d["ego_primary_label"]);
    names = names.slice(0, 20)
    var selected: string = "normoc";
</script>

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

<div class="selection">
    <b>Species:</b>
    {#each names as name}
    <label>
        <input type="radio" bind:group={selected} name="names" value={name}> {name}
    </label>
    {/each}
</div>

<h5>Distances</h5>
<img src="https://storage.googleapis.com/birdclef-2023/data/processed/birdclef-2022/birdnet-embeddings-with-neighbors-static/v1/{selected}/distances.png">
<h5>Ego Birdnet Label</h5>
<img src="https://storage.googleapis.com/birdclef-2023/data/processed/birdclef-2022/birdnet-embeddings-with-neighbors-static/v1/{selected}/ego_birdnet_label.png">
<h5>KNN Birdnet Label</h5>
<img src="https://storage.googleapis.com/birdclef-2023/data/processed/birdclef-2022/birdnet-embeddings-with-neighbors-static/v1/{selected}/knn_birdnet_label.png">
