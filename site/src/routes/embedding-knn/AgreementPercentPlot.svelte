<script lang="ts">
  import Plot from "$lib/Plot.svelte";
  export let data: any[] = [];

  function transform(data: any[]) {
    return [
      {
        x: data.map((d) => d["pct_ego_birdnet_label_matches"]),
        y: data.map((d) => d["pct_knn_birdnet_label_matches"]),
        // also include annotation for each point
        text: data.map((d) => d["ego_primary_label"]),
        mode: "markers",
        type: "scatter",
        textposition: "top center",
      },
      {
        x: [0, 1],
        y: [0.5, 0.5],
        mode: "lines",
        line: {
          color: "orange",
          dash: "dash",
        },
      },
      {
        x: [0.5, 0.5],
        y: [0, 1],
        mode: "lines",
        line: {
          color: "orange",
          dash: "dash",
        },
      },
    ];
  }

  $: layout = {
    xaxis: {
      title: "Percent of ego birdnet label matches",
      range: [0, 1],
    },
    yaxis: {
      title: "Percent of knn birdnet label matches",
      range: [0, 1],
    },
    title: "Percent of ego and knn birdnet label matches",
    // no legend
    showlegend: false,
  };
</script>

<Plot {data} {transform} {layout} />
