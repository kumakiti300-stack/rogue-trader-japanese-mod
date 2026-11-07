using HarmonyLib;
using Kingmaker.Enums;
using Kingmaker.Localization;
using Kingmaker.Localization.Enums;
using Kingmaker.UnitLogic.UI;

namespace RTJP.DisplayFix
{
    [HarmonyPatch(typeof(UIPropertySettings), "get_PropertyName")]
    internal static class GalvanicGateTooltipPatch
    {
        private const string FeatureGuid = "e895e579fb5a4eeaa9608675b86d50cb";

        [HarmonyPostfix]
        internal static void Postfix(UIPropertySettings __instance, ref ContextPropertyName? __result)
        {
            var localization = LocalizationManager.Instance;
            if (localization == null || localization.CurrentLocale != Locale.jaJP || __instance == null)
                return;

            string key = __instance.LinkKey;
            bool damage = key == "DamageBonus" && __result == ContextPropertyName.Value2;
            bool penetration = key == "ArmorPenetration" && __result == ContextPropertyName.Bonus1;
            if (!damage && !penetration)
                return;

            var source = __instance.PropertySource;
            if (source == null || source.AssetGuid.ToString() != FeatureGuid)
                return;

            // The feature defines Value1 = INT bonus and Value2 = Tech-Use / 10.
            // Its applied buff uses those formulas for shock damage and armour
            // penetration respectively. Only the tooltip getter is corrected;
            // neither the stored blueprint settings nor combat calculations change.
            __result = damage ? ContextPropertyName.Value1 : ContextPropertyName.Value2;
        }
    }
}
