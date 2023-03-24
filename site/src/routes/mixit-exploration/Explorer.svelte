<script>
  const url_prefix = "/api/v1/data/processed/mixit_visualize_subset";
  export let track_name;
  $: track_id = track_name.replace(".ogg", "");
</script>

<!-- add audio tracks for the original and source0 to source3 -->
<h1>{track_id}</h1>

<audio controls>
  <source src="{url_prefix}/audio/{track_id}.mp3" type="audio/mpeg" />
</audio>
