using UnityEngine;

/// <summary>
/// Fires projectiles from a muzzle transform while the fire button is held,
/// limited by a fire rate. Aims along the muzzle's right (+X) axis.
/// </summary>
public class PlayerShooter : MonoBehaviour
{
    [Header("Weapon")]
    [SerializeField] private Projectile projectilePrefab;
    [SerializeField] private Transform muzzle;
    [SerializeField] private float shotsPerSecond = 6f;

    private float nextShotTime;

    private void Update()
    {
        // "Fire1" is part of the default legacy Input Manager setup.
        if (Input.GetButton("Fire1") && Time.time >= nextShotTime)
        {
            Fire();
        }
    }

    private void Fire()
    {
        if (projectilePrefab == null || muzzle == null)
        {
            Debug.LogWarning("PlayerShooter: assign a projectile prefab and muzzle.", this);
            return;
        }

        nextShotTime = Time.time + 1f / Mathf.Max(0.01f, shotsPerSecond);
        Instantiate(projectilePrefab, muzzle.position, muzzle.rotation);
    }
}
