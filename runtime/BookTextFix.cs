using System;
using System.Reflection;
using HarmonyLib;
using Kingmaker.Localization;
using Kingmaker.Localization.Enums;
using Kingmaker.Modding;
using Kingmaker.UI.Common;

[assembly: AssemblyVersion("0.1.7.0")]

namespace RTJP.DisplayFix
{
    public static class BookTextFix
    {
        [OwlcatModificationEnterPoint]
        public static void Initialize(OwlcatModification modification)
        {
            try
            {
                new Harmony("RTJP.JapaneseBookText").PatchAll(typeof(BookTextFix).Assembly);
                modification.Logger.Log("Japanese book-text initial-letter fix enabled.");
            }
            catch (Exception error)
            {
                // A changed game API must not prevent the translation pack loading.
                modification.Logger.Error("Could not enable book-text display fix: " + error);
            }
        }
    }

    [HarmonyPatch(typeof(UIUtility), nameof(UIUtility.GetBookFormat))]
    internal static class JapaneseBookFormatPatch
    {
        [HarmonyPrefix]
        internal static bool Prefix(string __0, ref string __result)
        {
            var localization = LocalizationManager.Instance;
            if (localization == null || localization.CurrentLocale != Locale.jaJP)
                return true;

            // GetBookFormat adds its own font, size and vertical-offset tags to
            // the first letter. Japanese glyphs need the normal paragraph style.
            // Returning the input also preserves existing links and other markup.
            __result = __0;
            return false;
        }
    }
}
