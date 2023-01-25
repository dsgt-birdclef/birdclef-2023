<script lang="ts">
  import Plot from "$lib/Plot.svelte";
  export let data: any[] = [];

  function transform(data: any[]) {
    return [
      {
        x: data.map((d) => d["n_ego_birdnet_label_matches"]),
        y: data.map((d) => d["n_knn_birdnet_label_matches"]),
        // also include annotation for each point
        text: data.map((d) => d["ego_primary_label"]),
        mode: "markers",
        type: "scatter",
        textposition: "top center",
      },
    ];
  }

  $: layout = {
    xaxis: {
      title: "Count of ego birdnet label matches",
      type: "log",
    },
    yaxis: {
      title: "Count of knn birdnet label matches",
      type: "log",
    },
    title: "Count of ego and knn birdnet label matches",
  };
</script>

<Plot {data} {transform} {layout} />
