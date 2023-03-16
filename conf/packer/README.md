# packer

This generates an ubuntu 22.04 image using the `batch` and `dev` ansible roles.
It is written to the `birdclef-cloud-batch` image family.

```bash
packer init .
packer build .
```

```
==> Wait completed after 22 minutes 24 seconds

==> Builds finished. The artifacts of successful builds are:
--> googlecompute.birdclef-cloud-batch: A disk image was created: birdclef-cloud-batch-1678341546
```
