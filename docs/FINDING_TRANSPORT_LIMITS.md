# Finding transport resource limits

Finding canonicalization and body hashing first enforce a bounded iterative walk: at most
4,096 JSON nodes (including object keys), 65,536 total string/key characters, and 64 nesting
levels. A container is checked before its children are queued. Hashing applies the same guard
before copying the body. These limits bound temporary serialization memory even for unknown
fields that the structural schema will subsequently reject.

The limits are deliberately larger than the closed Product finding contract and preserve its
canonical fixture bytes. They do not change the Product schema, source artifact size limits,
existing bundle serialization, or the representation of missing measurements.

Regression tests cover oversized strings and keys, wide arrays, aggregate text, cyclic input,
and refusal before deepcopy. The frozen producer fixture and all canonical number vectors
remain unchanged.
