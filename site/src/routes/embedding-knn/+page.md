<script>
    import AgreementTable from "./AgreementTable.svelte";
    export let data;
    $: agreement = data.agreement;
</script>

# embedding knn

<AgreementTable data={agreement} />
