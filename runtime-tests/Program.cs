// API substitutes are confined to this test executable, never the release DLL.
using System;
using System.Collections.Generic;
using System.Reflection;
using Kingmaker.Localization;
using Kingmaker.Localization.Enums;
using Kingmaker.Modding;
using RTJP.DisplayFix;
using Kingmaker.Enums;
using Kingmaker.UnitLogic.UI;
using Kingmaker.UnitLogic.Mechanics.Blueprints;

internal static class Program
{
    private static int checks;
    private static void Check(bool value)
    {
        checks++;
        if (!value) throw new Exception("Display-fix regression check " + checks);
    }

    private static void Main()
    {
        var manager = new LocalizationManager();
        LocalizationManager.Instance = manager;
        manager.CurrentLocale = Locale.jaJP;
        foreach (var input in new[] {
            "ローグトレーダーがアトリウムの奥へ進むほど、足取りが危うくなっていく。",
            "ローグトレーダーはメディカエ・デッキに運び込まれ、医師たちに取り囲まれる。",
            "<color=#123456><i>「本文」</i></color>\n\n次の段落",
            "{n}{name}は{g|Encyclopedia:test}ここ{/g}を読む。{/n}",
            "  前後の空白  ", "𠮷と絵文字🙂", "", null
        })
        {
            string result = "unchanged sentinel";
            Check(!JapaneseBookFormatPatch.Prefix(input, ref result));
            Check(object.ReferenceEquals(input, result));
        }
        foreach (Locale locale in Enum.GetValues(typeof(Locale)))
        {
            if (locale == Locale.jaJP) continue;
            manager.CurrentLocale = locale;
            string result = "unchanged sentinel";
            Check(JapaneseBookFormatPatch.Prefix("The Rogue Trader walks...", ref result));
            Check(result == "unchanged sentinel");
        }
        // Check every call uses the current language, including a live switch back.
        manager.CurrentLocale = Locale.jaJP;
        string switched = null;
        Check(!JapaneseBookFormatPatch.Prefix("本文", ref switched) && switched == "本文");
        LocalizationManager.Instance = null;
        Check(JapaneseBookFormatPatch.Prefix("本文", ref switched));

        var target = (HarmonyLib.HarmonyPatch)Attribute.GetCustomAttribute(
            typeof(JapaneseBookFormatPatch), typeof(HarmonyLib.HarmonyPatch));
        Check(target.Target == typeof(Kingmaker.UI.Common.UIUtility));
        Check(target.Method == "GetBookFormat");
        Check(Attribute.IsDefined(typeof(JapaneseBookFormatPatch).GetMethod("Prefix",
            BindingFlags.NonPublic | BindingFlags.Static), typeof(HarmonyLib.HarmonyPrefix)));
        Check(Attribute.IsDefined(typeof(BookTextFix).GetMethod("Initialize"),
            typeof(OwlcatModificationEnterPointAttribute)));
        var modification = new OwlcatModification();
        BookTextFix.Initialize(modification);
        Check(HarmonyLib.Harmony.Id == "RTJP.JapaneseBookText");
        Check(HarmonyLib.Harmony.Assembly == typeof(BookTextFix).Assembly);
        Check(modification.Logger.Messages.Count == 1);
        HarmonyLib.Harmony.Fail = true;
        BookTextFix.Initialize(modification);
        Check(modification.Logger.Errors.Count == 1);
        CheckGalvanicGate();
        Console.WriteLine(checks + " display-fix regression checks passed (API substitutes).");
    }

    private static void CheckGalvanicGate()
    {
        LocalizationManager.Instance = new LocalizationManager { CurrentLocale = Locale.jaJP };
        const string feature = "e895e579fb5a4eeaa9608675b86d50cb";
        var source = new BlueprintMechanicEntityFact { AssetGuid = feature };
        var ui = new UIPropertySettings { LinkKey = "ArmorPenetration", PropertySource = source };
        ContextPropertyName? result = ContextPropertyName.Bonus1;
        GalvanicGateTooltipPatch.Postfix(ui, ref result);
        Check(result == ContextPropertyName.Value2);
        ui.LinkKey = "DamageBonus";
        result = ContextPropertyName.Value2;
        GalvanicGateTooltipPatch.Postfix(ui, ref result);
        Check(result == ContextPropertyName.Value1);

        // A different feature or a third-party correction must keep its value.
        foreach (string guid in new[] { feature, "other-feature" })
        foreach (string key in new[] { "DamageBonus", "ArmorPenetration", "AbilityRange", "other", null })
        foreach (ContextPropertyName? original in new ContextPropertyName?[] {
            ContextPropertyName.Value1, ContextPropertyName.Value2, ContextPropertyName.Bonus1, null })
        {
            source.AssetGuid = guid;
            ui.LinkKey = key;
            result = original;
            GalvanicGateTooltipPatch.Postfix(ui, ref result);
            var expected = original;
            if (guid == feature && key == "DamageBonus" && original == ContextPropertyName.Value2)
                expected = ContextPropertyName.Value1;
            if (guid == feature && key == "ArmorPenetration" && original == ContextPropertyName.Bonus1)
                expected = ContextPropertyName.Value2;
            Check(result == expected);
        }
        source.AssetGuid = feature;
        ui.LinkKey = "ArmorPenetration";
        foreach (Locale locale in Enum.GetValues(typeof(Locale)))
        {
            LocalizationManager.Instance.CurrentLocale = locale;
            result = ContextPropertyName.Bonus1;
            GalvanicGateTooltipPatch.Postfix(ui, ref result);
            Check(result == (locale == Locale.jaJP ? ContextPropertyName.Value2 : ContextPropertyName.Bonus1));
        }
        LocalizationManager.Instance.CurrentLocale = Locale.jaJP;
        ui.PropertySource = null;
        result = ContextPropertyName.Bonus1;
        GalvanicGateTooltipPatch.Postfix(ui, ref result);
        Check(result == ContextPropertyName.Bonus1);
        GalvanicGateTooltipPatch.Postfix(null, ref result);
        Check(result == ContextPropertyName.Bonus1);
        ui.PropertySource = source;
        LocalizationManager.Instance = null;
        GalvanicGateTooltipPatch.Postfix(ui, ref result);
        Check(result == ContextPropertyName.Bonus1);
    }
}

namespace Kingmaker.Localization.Enums
{
    public enum Locale { enGB, ruRU, deDE, frFR, zhCN, esES, jaJP, trTR, Sound, dev }
}
namespace Kingmaker.Localization
{
    public class LocalizationManager
    {
        public static LocalizationManager Instance;
        public Locale CurrentLocale;
    }
}
namespace Kingmaker.UI.Common { public static class UIUtility { public static void GetBookFormat() {} } }
namespace Kingmaker.Enums { public enum ContextPropertyName { Value1, Value2, Bonus1 } }
namespace Kingmaker.UnitLogic.Mechanics.Blueprints
{
    public class BlueprintMechanicEntityFact { public string AssetGuid; }
}
namespace Kingmaker.UnitLogic.UI
{
    public class UIPropertySettings
    {
        public string LinkKey;
        public BlueprintMechanicEntityFact PropertySource;
        public ContextPropertyName? PropertyName { get { return ContextPropertyName.Bonus1; } }
    }
}
namespace Kingmaker.Modding
{
    [AttributeUsage(AttributeTargets.Method)]
    public class OwlcatModificationEnterPointAttribute : Attribute {}
    public class OwlcatModification { public TestLogger Logger = new TestLogger(); }
    public class TestLogger
    {
        public List<string> Messages = new List<string>();
        public List<string> Errors = new List<string>();
        public void Log(string message) { Messages.Add(message); }
        public void Error(string message) { Errors.Add(message); }
    }
}
namespace HarmonyLib
{
    [AttributeUsage(AttributeTargets.Class)]
    public class HarmonyPatch : Attribute
    {
        public Type Target; public string Method;
        public HarmonyPatch(Type target, string method) { Target = target; Method = method; }
    }
    [AttributeUsage(AttributeTargets.Method)] public class HarmonyPrefix : Attribute {}
    [AttributeUsage(AttributeTargets.Method)] public class HarmonyPostfix : Attribute {}
    public class Harmony
    {
        public static string Id; public static Assembly Assembly; public static bool Fail;
        public Harmony(string id) { Id = id; }
        public void PatchAll(Assembly assembly)
        {
            if (Fail) throw new MissingMethodException("test game API change");
            Assembly = assembly;
        }
    }
}
