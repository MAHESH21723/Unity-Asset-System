using TMPro;
using UnityEngine;

/// <summary>
/// Switches between the main menu and HUD panels and updates a status label.
/// Requires the TextMeshPro package (installed by default in most templates).
/// </summary>
public class UIManager : MonoBehaviour
{
    public static UIManager Instance { get; private set; }

    [SerializeField] private GameObject menuPanel;
    [SerializeField] private GameObject hudPanel;
    [SerializeField] private TMP_Text statusText;

    private void Awake()
    {
        if (Instance != null && Instance != this)
        {
            Destroy(gameObject);
            return;
        }

        Instance = this;
    }

    public void ShowMainMenu()
    {
        SetPanels(menuVisible: true);
    }

    public void StartGameplayUI()
    {
        SetPanels(menuVisible: false);
    }

    public void SetStatusText(string text)
    {
        if (statusText != null)
        {
            statusText.text = text;
        }
    }

    private void SetPanels(bool menuVisible)
    {
        if (menuPanel != null) menuPanel.SetActive(menuVisible);
        if (hudPanel != null) hudPanel.SetActive(!menuVisible);
    }
}
