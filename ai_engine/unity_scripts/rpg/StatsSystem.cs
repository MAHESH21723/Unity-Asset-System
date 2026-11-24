using UnityEngine;

/// <summary>
/// Character stats with experience-based levelling and defense-reduced damage.
/// </summary>
public class StatsSystem : MonoBehaviour
{
    [Header("Base Stats")]
    [SerializeField] private int level = 1;
    [SerializeField] private int experience;
    [SerializeField] private int baseMaxHealth = 100;
    [SerializeField] private int strength = 10;
    [SerializeField] private int defense = 5;

    public int Level => level;
    public int Strength => strength;
    public int CurrentHealth { get; private set; }
    public int MaxHealth => baseMaxHealth;
    public bool IsDead => CurrentHealth <= 0;

    private void Awake()
    {
        CurrentHealth = baseMaxHealth;
    }

    public void AddExperience(int amount)
    {
        experience += amount;

        // Each level needs level * 100 XP; loop handles multiple level-ups.
        while (experience >= level * 100)
        {
            experience -= level * 100;
            LevelUp();
        }
    }

    private void LevelUp()
    {
        level++;
        baseMaxHealth += 15;
        CurrentHealth = baseMaxHealth;
        strength += 2;
        defense += 1;
        Debug.Log($"Leveled up! Now level {level}.");
    }

    public void TakeDamage(int rawDamage)
    {
        if (IsDead) return;

        int netDamage = Mathf.Max(1, rawDamage - defense);
        CurrentHealth = Mathf.Max(0, CurrentHealth - netDamage);
        Debug.Log($"Took {netDamage} damage. HP: {CurrentHealth}/{baseMaxHealth}");

        if (IsDead)
        {
            Die();
        }
    }

    private void Die()
    {
        Debug.Log("Character has died.");
    }
}
