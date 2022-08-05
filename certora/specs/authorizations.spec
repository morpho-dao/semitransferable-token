methods {
    totalSupply() returns (uint256) envfree
    balanceOf(address) returns (uint256) envfree
    allowance(address, address) returns (uint256) envfree
    owner() returns (address) envfree
    getUserRoles(address) returns (uint256) envfree
    isCapabilityPublic(uint32) returns (bool) envfree
    getRolesWithCapability(uint32) returns (uint256) envfree
    doesUserHaveRole(address, uint8) returns (bool) envfree
    doesRoleHaveCapability(uint8, uint32) returns (bool) envfree
}


// UNDERLYING FUNCTIONS

// rule transferSameAsUnderlyingFunction() {
//     env e; address to; uint256 amount;

//     storage initial = lastStorage;
//     transfer(e, to, amount);
//     storage afterTransfer = lastStorage;

//     underlyingTransfer(e, to, amount) at initial;
//     storage afterUnderlyingTransfer = lastStorage;

//     assert(afterTransfer == afterUnderlyingTransfer);
// }


// AUTHORIZATION STORAGE 

// The authorization variables are: owner, isCapabilityPublic, getUserRoles and getRolesCapability.

// owner variable

rule ownerChanging() {
    env e;
    method f; calldataarg args; uint32 newOwner;
    address ownerBefore = owner();

    f(e, args);

    address ownerAfter = owner();
    assert (ownerAfter != ownerBefore =>
            f.selector == setOwner(address).selector);
}

rule setOwnerShouldChangeOwner(address newOwner) {
    env e;

    setOwner(e, newOwner);

    address ownerAfter = owner();
    assert (ownerAfter == newOwner);
}

// isCapabilityPublic mapping

rule isCapabilityPublicChanging() {
    env e;
    method f; calldataarg args; uint32 capability;
    bool capabilityPublicBefore = isCapabilityPublic(capability);

    f(e, args);

    bool capabilityPublicAfter = isCapabilityPublic(capability);
    assert (capabilityPublicAfter != capabilityPublicBefore =>
            f.selector == setPublicCapability(uint32, bool).selector);
}

rule setPublicCapabilityShouldChangeIsPublicCapability(uint32 capability, bool enabled) {
    env e;

    setPublicCapability(e, capability, enabled);

    bool capabilityIsPublicAfter = isCapabilityPublic(capability);
    assert (capabilityIsPublicAfter == enabled);
}

// getUserRoles mapping

rule getUserRolesChanging() {
    env e;
    method f; calldataarg args; address user;
    uint256 userRolesBefore = getUserRoles(user);

    f(e, args);

    uint userRolesAfter = getUserRoles(user);
    assert (userRolesAfter != userRolesBefore =>
            f.selector == setUserRole(address, uint8, bool).selector);
}

rule setUserRoleShouldChangeDoesUserHaveRole(address user, uint8 role, bool enabled) {
    env e;

    setUserRole(e, user, role, enabled);

    bool userHasRoleAfter = doesUserHaveRole(user, role);
    assert (userHasRoleAfter == enabled);
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

rule doesUserHaveRoleChangingArgs(address userChanged, uint8 roleChanged, bool enabledChanged) {
    env e;
    address user; uint8 role;
    bool userHasRoleBefore = doesUserHaveRole(user, role);

    setUserRole(e, userChanged, roleChanged, enabledChanged);

    bool userHasRoleAfter = doesUserHaveRole(user, role);
    assert (userHasRoleAfter != userHasRoleBefore =>
            userChanged == user && roleChanged == role);
}

// getRolesWithCapability mapping

rule getRolesWithCapabilityChanging() {
    env e;
    method f; calldataarg args; uint32 capability;
    uint256 rolesBefore = getRolesWithCapability(capability);

    f(e, args);

    uint256 rolesAfter = getRolesWithCapability(capability);
    assert (rolesAfter != rolesBefore =>
            f.selector == setRoleCapability(uint8, uint32, bool).selector);
}

rule setRoleCapabilityShouldChangeDoesRoleHaveCapability(uint8 role, uint32 capability, bool enabled) {
    env e;

    setRoleCapability(e, role, capability, enabled);

    bool roleHasCapabilityAfter = doesRoleHaveCapability(role, capability);
    assert (roleHasCapabilityAfter == enabled);
}

rule doesRoleHaveCapabilityChangingMethod() {
    env e;
    method f; calldataarg args; uint8 role; uint32 capability;
    bool roleHasCapabilityBefore = doesRoleHaveCapability(role, capability);

    f(e, args);

    bool roleHasCapabilityAfter = doesRoleHaveCapability(role, capability);
    assert (roleHasCapabilityAfter != roleHasCapabilityBefore =>
            f.selector == setRoleCapability(uint8, uint32, bool).selector);
}

rule doesRoleHaveCapabilityChangingArgs(uint8 roleChanged, uint32 capabilityChanged, bool enabledChanged) {
    env e;
    uint8 role; uint32 capability;
    bool roleHasCapabilityBefore = doesRoleHaveCapability(role, capability);

    setRoleCapability(e, roleChanged, capabilityChanged, enabledChanged);

    bool roleHasCapabilityAfter = doesRoleHaveCapability(role, capability);
    assert (roleHasCapabilityAfter != roleHasCapabilityBefore =>
            roleChanged == role && capabilityChanged == capability);
}


// AUTHORIZATION FUNCTIONS

// Compute the set of all the functions that need authorization.
rule allFunctionsNeedingAuthorization() {
    env e;
    storage initialState = lastStorage;
    method f; calldataarg args;

    f@withrevert(e, args);
    bool revertNormal = lastReverted;

    env e_auth; bool enabled;
    setPublicCapability(e_auth, f.selector, enabled) at initialState;
    f@withrevert(e, args);
    bool revertOwner = lastReverted;

    assert ((revertOwner != revertNormal) =>
            (f.selector == setOwner(address).selector) ||
             f.selector == setPublicCapability(uint32, bool).selector ||
             f.selector == setUserRole(address, uint8, bool).selector ||
             f.selector == setRoleCapability(uint8, uint32, bool).selector ||
             f.selector == transfer(address, uint256).selector ||
             f.selector == transferFrom(address, address, uint256).selector ||
             f.selector == mint(address, uint256).selector);
}


// Compute the set of all functions able to change the authorizations.
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
//              authFunction.selector == setPublicCapability(uint32, bool).selector ||
//              authFunction.selector == setUserRole(address, uint8, bool).selector ||
//              authFunction.selector == setRoleCapability(uint8, uint32, bool).selector ||
//              authFunction.selector == transfer(address, uint256).selector ||
//              authFunction.selector == transferFrom(address, address, uint256).selector ||
//              authFunction.selector == mint(address, uint256).selector);
// }


// AUTHORIZATION CONDITIONS

definition userIsRoleAuthorizedForCapability(address user, uint8 role, uint32 capability) returns bool =
    user == owner() || 
    isCapabilityPublic(capability) || 
    doesUserHaveRole(user, role) && doesRoleHaveCapability(role, capability);


rule transferRevertingConditions(address to, uint256 amount) {
    env e; uint8 role;
    require (e.msg.value == 0);
    require userIsRoleAuthorizedForCapability(e.msg.sender, role, transfer(address, uint256).selector);

    storage initialState = lastStorage;
    underlyingTransfer@withrevert(e, to, amount);
    bool revertAfterUnderlyingTransfer = lastReverted;

    transfer@withrevert(e, to, amount) at initialState;
    bool revertAfterTransfer = lastReverted;

    assert (revertAfterTransfer <=> revertAfterUnderlyingTransfer);
}

rule transferFromRevertingConditions(address from, address to, uint256 amount) {
    env e; uint8 role;
    require (e.msg.value == 0);
    require userIsRoleAuthorizedForCapability(e.msg.sender, role, transferFrom(address, address, uint256).selector);

    storage initialState = lastStorage;
    underlyingTransferFrom@withrevert(e, from, to, amount);
    bool revertAfterUnderlyingTransferFrom = lastReverted;

    transferFrom@withrevert(e, from, to, amount) at initialState;
    bool revertAfterTransferFrom = lastReverted;

    assert (revertAfterTransferFrom <=> revertAfterUnderlyingTransferFrom);
}

rule mintRevertingConditions(address to, uint256 amount) {
    env e; uint8 role;
    require (e.msg.value == 0);
    require userIsRoleAuthorizedForCapability(e.msg.sender, role, mint(address, uint256).selector);

    storage initialState = lastStorage;
    underlyingMint@withrevert(e, to, amount);
    bool revertAfterUnderlyingMint = lastReverted;

    mint@withrevert(e, to, amount) at initialState;
    bool revertAfterMint = lastReverted;

    assert (revertAfterMint <=> revertAfterUnderlyingMint);
}
