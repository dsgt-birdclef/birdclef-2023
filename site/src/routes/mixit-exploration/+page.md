<script>
    import Explorer from "./Explorer.svelte";
    import Table from "$lib/Table.svelte";
    export let data;
    $: options = {autoColumns:true, pagination: "local", paginationSize: 4};
</script>

# mixit exploration

You can explore the results of running mixit on a small subset of 30 second training examples from the 2023 dataset.

<Table data={data.subset} {options} />

<Explorer track_name={data.subset[0].filename} />
