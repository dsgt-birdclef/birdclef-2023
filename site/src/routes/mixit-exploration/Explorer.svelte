<script>
  const url_prefix = "/api/v1/data/processed/mixit_visualize_subset";
  export let track_name;
  export let detailed_view;
  $: track_id = track_name.replace(".ogg", "");
  $: stem = track_id.split("/")[1];
</script>

<h2>{track_id}</h2>

{#if !detailed_view}
  <audio controls src="{url_prefix}/audio/{track_id}.mp3" preload="none" />
  <img alt="spectrogram" src="{url_prefix}/assets/{track_id}/{stem}_spectrogram.png" />
  {#each [0, 1, 2, 3] as i}
    <audio controls src="{url_prefix}/audio/{track_id}_source{i}.mp3" preload="none" />
    <img alt="spectrogram" src="{url_prefix}/assets/{track_id}/{stem}_source{i}_spectrogram.png" />
  {/each}
{:else}
  <h3>source</h3>
  <audio controls src="{url_prefix}/audio/{track_id}.mp3" preload="none" />
  <img alt="spectrogram" src="{url_prefix}/assets/{track_id}/{stem}_spectrogram.png" />

  {#each [0, 1, 2, 3] as i}
    <h3>mixit channel {i}</h3>
    <audio controls src="{url_prefix}/audio/{track_id}_source{i}.mp3" preload="none" />
    <img alt="spectrogram" src="{url_prefix}/assets/{track_id}/{stem}_source{i}_spectrogram.png" />
    <img alt="top5" src="{url_prefix}/assets/{track_id}/{stem}_source{i}_top5.png" />
  {/each}
{/if}
