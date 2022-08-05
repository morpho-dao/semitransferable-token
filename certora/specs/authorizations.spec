methods {
    totalSupply() returns (uint256) envfree
    balanceOf(address) returns (uint256) envfree
    allowance(address, address) returns (uint256) envfree
    owner() returns (address) envfree
    getUserRoles(address) returns (bytes32) envfree
    isCapabilityPublic(bytes4) returns (bool) envfree
    getRolesWithCapability(bytes4) returns (bytes32) envfree
    doesUserHaveRole(address, uint8) returns (bool) envfree
    doesRoleHaveCapability(uint8, bytes4) returns (bool) envfree
    to_bytes4(uint32) returns (bytes4) envfree
}

// The following functions are called the authorization functions:
// setOwner, setPublicCapability, setUserRole and setRoleCapability.


// AUTHORIZATION OVERVIEW

// Check that only the authorization functions are able to change the authorization storage.

rule ownerChanging() {
    env e;
    method f; calldataarg args; bytes4 newOwner;
    address ownerBefore = owner();

    f(e, args);

    address ownerAfter = owner();
    assert (ownerAfter != ownerBefore =>
            f.selector == setOwner(address).selector);
}

rule setOwnerShouldChangeOwner() {
    env e;
    address newOwner;

    setOwner(e, newOwner);

    address ownerAfter = owner();
    assert (ownerAfter == newOwner);
}

rule isCapabilityPublicChanging() {
    env e;
    method f; calldataarg args; bytes4 capability;
    bool capabilityPublicBefore = isCapabilityPublic(capability);

    f(e, args);

    bool capabilityPublicAfter = isCapabilityPublic(capability);
    assert (capabilityPublicAfter != capabilityPublicBefore =>
            f.selector == setPublicCapability(bytes4, bool).selector);
}

rule setPublicCapabilityShouldChangeIsPublicCapability() {
    env e;
    bytes4 capability; bool enabled;

    setPublicCapability(e, capability, enabled);

    bool capabilityIsPublicAfter = isCapabilityPublic(capability);
    assert (capabilityIsPublicAfter == enabled);
}

rule getUserRolesChanging() {
    env e;
    method f; calldataarg args; address user;
    bytes32 userRolesBefore = getUserRoles(user);

    f(e, args);

    bytes32 userRolesAfter = getUserRoles(user);
    assert (userRolesAfter != userRolesBefore =>
            f.selector == setUserRole(address, uint8, bool).selector);
}

rule doesUserHaveRoleChangingMethod() {
    env e;
    method f; calldataarg args; address user; uint8 role;
    bool userHasRoleBefore = doesUserHaveRole(user, role);

    f(e, args);

    bool userHasRoleAfter = doesUserHaveRole(user, role);
    assert (userHasRoleAfter != userHasRoleBefore =>
            f.selector == setUserRole(address, uint8, bool).selector);
}

rule doesUserHaveRoleChangingArgs() {
    env e;
    address userChanged; uint8 roleChanged; bool enabledChanged;
    address user; uint8 role;
    bool userHasRoleBefore = doesUserHaveRole(user, role);

    setUserRole(e, userChanged, roleChanged, enabledChanged);

    bool userHasRoleAfter = doesUserHaveRole(user, role);
    assert (userHasRoleAfter != userHasRoleBefore =>
            userChanged == user && roleChanged == role && userHasRoleAfter == enabledChanged);
}

rule getRolesWithCapabilityChanging() {
    env e;
    method f; calldataarg args; bytes4 capability;
    bytes32 rolesBefore = getRolesWithCapability(capability);

    f(e, args);

    bytes32 rolesAfter = getRolesWithCapability(capability);
    assert (rolesAfter != rolesBefore =>
            f.selector == setRoleCapability(uint8, bytes4, bool).selector);
}

rule doesRoleHaveCapabilityChangingMethod() {
    env e;
    method f; calldataarg args; uint8 role; bytes4 capability;
    bool roleHasCapabilityBefore = doesRoleHaveCapability(role, capability);

    f(e, args);

    bool roleHasCapabilityAfter = doesRoleHaveCapability(role, capability);
    assert (roleHasCapabilityAfter != roleHasCapabilityBefore =>
            f.selector == setRoleCapability(uint8, bytes4, bool).selector);
}

rule doesRoleHaveCapabilityChangingArgs() {
    env e;
    uint8 roleChanged; bytes4 capabilityChanged; bool enabledChanged; uint8 role; bytes4 capability;
    bool roleHasCapabilityBefore = doesRoleHaveCapability(role, capability);

    setRoleCapability(e, roleChanged, capabilityChanged, enabledChanged);

    bool roleHasCapabilityAfter = doesRoleHaveCapability(role, capability);
    assert (roleHasCapabilityAfter != roleHasCapabilityBefore =>
            roleChanged == role && capabilityChanged == capability && roleHasCapabilityAfter == enabledChanged);
}

// Compute the set of authorization functions and the set of functions needing authorization.

// Check that all the functions that need authorization are the following:
// the authorization functions and transfer, transferFrom and mint.
rule allFunctionsNeedingAuthorization() {
    env e;
    storage initialState = lastStorage;
    method f; calldataarg args;

    f@withrevert(e, args);
    bool revertNormal = lastReverted;

    env e_auth; bool enabled;
    setPublicCapability(e_auth, to_bytes4(f.selector), enabled) at initialState;
    f@withrevert(e, args);
    bool revertOwner = lastReverted;

    assert ((revertOwner != revertNormal) =>
            (f.selector == setOwner(address).selector) ||
             f.selector == setPublicCapability(bytes4, bool).selector ||
             f.selector == setUserRole(address, uint8, bool).selector ||
             f.selector == setRoleCapability(uint8, bytes4, bool).selector ||
             f.selector == transfer(address, uint256).selector ||
             f.selector == transferFrom(address, address, uint256).selector ||
             f.selector == mint(address, uint256).selector);
}


// Check that the functions able to change the function authorizations are the authorization functions.
// This rule can't be checked for now by the Certora tool because there is no way to discriminate on the revert reason. Thus it can fail because the underlying functions reverts.
// rule allAuthorizationFunctions() {
//     env e_auth; env e;
//     storage initialState = lastStorage;
//     method authFunction; calldataarg argsAuth;
//     method f; calldataarg args;

//     f@withrevert(e, args);
//     bool revertWithoutAuth = lastReverted; // would need to be able to check if the revert reason is "UNAUTHORIZED".

//     authFunction(e_auth, argsAuth) at initialState;
//     f@withrevert(e, args);
//     bool revertWithAuth = lastReverted; // would need to be able to check if the revert reason is "UNAUTHORIZED".

//     assert ((revertWithAuth != revertWithoutAuth) =>
//             (authFunction.selector == setOwner(address).selector) ||
//              authFunction.selector == setPublicCapability(bytes4, bool).selector ||
//              authFunction.selector == setUserRole(address, uint8, bool).selector ||
//              authFunction.selector == setRoleCapability(uint8, bytes4, bool).selector ||
//              authFunction.selector == transfer(address, uint256).selector ||
//              authFunction.selector == transferFrom(address, address, uint256).selector ||
//              authFunction.selector == mint(address, uint256).selector);
// }


// OWNER AUTHORIZATION

// Check that the owner is always authorized.
// See erc20reverts.spec to compare to the underlying function revert conditions.

rule ownerCanAlwaysTransfer() {
    env e;
    address sender; address to; uint256 amount;
    require (sender == e.msg.sender);
    require (sender == owner());
    uint256 balanceBefore = balanceOf(sender);
    require (e.msg.value == 0);

    transfer@withrevert(e, to, amount);

    assert (lastReverted <=> amount > balanceBefore);
}

rule ownerCanAlwaysTransferFrom() {
    env e;
    address sender; address from; address to; uint256 amount;
    require (sender == e.msg.sender);
    require (sender == owner());
    uint256 balanceBefore = balanceOf(from);
    uint256 allowanceBefore = allowance(from, sender);
    require (e.msg.value == 0);

    transferFrom@withrevert(e, from, to, amount);

    assert (lastReverted <=> amount > balanceBefore || amount > allowanceBefore);
}

rule ownerCanAlwaysMint() {
    env e;
    address sender; address to; uint256 amount;
    require (sender == e.msg.sender);
    require (sender == owner());
    uint256 totalSupply = totalSupply();
    require (e.msg.value == 0);

    mint@withrevert(e, to, amount);

    assert (lastReverted <=> totalSupply > max_uint256 - amount);
}


// PUBLIC AUTHORIZATION

// Check that public functions (as defined in RolesAuthority) are authorized.
// See erc20reverts.spec to compare to the underlying function revert conditions.

rule transferIsAuthorizedWhenPublicCapability() {
    env e;
    address sender; address to; uint256 amount;
    require (sender == e.msg.sender);
    uint256 balanceBefore = balanceOf(sender);
    require (e.msg.value == 0);

    require (isCapabilityPublic(to_bytes4(transfer(address, uint256).selector)));

    transfer@withrevert(e, to, amount);

    assert (lastReverted <=> amount > balanceBefore);
}

rule transferFromIsAuthorizedWhenPublicCapability() {
    env e;
    address sender; address from; address to; uint256 amount;
    require (sender == e.msg.sender);
    uint256 balanceBefore = balanceOf(from);
    uint256 allowanceBefore = allowance(from, sender);
    require (e.msg.value == 0);

    require (isCapabilityPublic(to_bytes4(transferFrom(address, address, uint256).selector)));

    transferFrom@withrevert(e, from, to, amount);

    assert (lastReverted <=> amount > balanceBefore || amount > allowanceBefore);
}

rule mintIsAuthorizedWhenPublicCapability() {
    env e;
    address sender; address to; uint256 amount;
    require (sender == e.msg.sender);
    uint256 totalSupply = totalSupply();
    require (e.msg.value == 0);

    require (isCapabilityPublic(to_bytes4(mint(address, uint256).selector)));

    mint@withrevert(e, to, amount);

    assert (lastReverted <=> totalSupply > max_uint256 - amount);
}


// ROLE AUTHORIZATION

// Check that users that have a role that has a capability for a function can call this function.
// See erc20reverts.spec to compare to the underlying function revert conditions.

rule transferIsAuthorizedWhenUserHasAppropriateRole() {
    env e;
    address sender; address to; uint256 amount; uint8 role;
    require (sender == e.msg.sender);
    uint256 balanceBefore = balanceOf(sender);
    require (e.msg.value == 0);

    require (doesUserHaveRole(sender, role));
    require (doesRoleHaveCapability(role, to_bytes4(transfer(address, uint256).selector)));

    transfer@withrevert(e, to, amount);

    assert (lastReverted <=> amount > balanceBefore);
}

rule transferFromIsAuthorizedWhenUserHasAppropriateRole() {
    env e;
    address sender; address from; address to; uint256 amount; uint8 role;
    require (sender == e.msg.sender);
    uint256 balanceBefore = balanceOf(from);
    uint256 allowanceBefore = allowance(from, sender);
    require (e.msg.value == 0);

    require (doesUserHaveRole(sender, role));
    require (doesRoleHaveCapability(role, to_bytes4(transferFrom(address, address, uint256).selector)));

    transferFrom@withrevert(e, from, to, amount);

    assert (lastReverted <=> amount > balanceBefore || amount > allowanceBefore);
}

rule mintIsAuthorizedWhenUserHasAppropriateRole() {
    env e;
    address sender; address to; uint256 amount; uint8 role;
    require (sender == e.msg.sender);
    uint256 totalSupply = totalSupply();
    require (e.msg.value == 0);

    require (doesUserHaveRole(sender, role));
    require (doesRoleHaveCapability(role, to_bytes4(mint(address, uint256).selector)));

    mint@withrevert(e, to, amount);

    assert (lastReverted <=> totalSupply > max_uint256 - amount);
}
