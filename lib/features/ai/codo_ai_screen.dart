import 'package:flutter/material.dart';

import '../../core/design/codo_colors.dart';
import '../../core/di/codo_services.dart';
import '../../core/widgets/codo_logo.dart';
import '../../core/widgets/source_required_card.dart';
import '../../domain/models/legal_models.dart';
import '../../domain/repositories/legal_repositories.dart';

class CodoAiScreen extends StatefulWidget {
  const CodoAiScreen({super.key});

  @override
  State<CodoAiScreen> createState() => _CodoAiScreenState();
}

class _CodoAiScreenState extends State<CodoAiScreen> {
  final controller = TextEditingController();
  String? question;
  CodoAnswer? answer;
  String? safeError;
  bool loading = false;
  CodoAnswerMode mode = CodoAnswerMode.simple;

  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }

  Future<void> _ask() async {
    final value = controller.text.trim();
    if (value.isEmpty || loading) return;
    setState(() {
      question = value;
      answer = null;
      safeError = null;
      loading = true;
    });
    controller.clear();
    try {
      final result = await CodoServicesScope.of(context).ai.answer(value, mode: mode);
      if (!mounted) return;
      setState(() => answer = result);
    } on VerifiedSourceUnavailable catch (e) {
      if (!mounted) return;
      setState(() => safeError = e.message);
    } catch (_) {
      if (!mounted) return;
      setState(() => safeError = 'La réponse ne peut pas être produite tant que les sources vérifiées ne sont pas disponibles.');
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: CodoLogo(compact: true)),
      body: Column(
        children: [
          Expanded(
            child: ListView(
              padding: const EdgeInsets.fromLTRB(20, 20, 20, 24),
              children: [
                Text('Demander à CODO', style: Theme.of(context).textTheme.headlineMedium),
                const SizedBox(height: 8),
                Text('CODO analyse une question uniquement après recherche dans le corpus juridique vérifié.', style: Theme.of(context).textTheme.bodySmall),
                const SizedBox(height: 16),
                DropdownButtonFormField<CodoAnswerMode>(
                  value: mode,
                  decoration: const InputDecoration(labelText: 'Niveau de réponse'),
                  items: CodoAnswerMode.values
                      .map((value) => DropdownMenuItem(value: value, child: Text(value.label)))
                      .toList(growable: false),
                  onChanged: loading ? null : (value) => setState(() => mode = value ?? CodoAnswerMode.simple),
                ),
                const SizedBox(height: 28),
                if (question == null)
                  const _AiIntro()
                else ...[
                  _QuestionBubble(question: question!),
                  const SizedBox(height: 20),
                  if (loading) const LinearProgressIndicator(),
                  if (safeError != null) SourceRequiredCard(detail: safeError),
                  if (answer != null) _AnswerView(answer: answer!),
                ],
              ],
            ),
          ),
          Container(
            padding: EdgeInsets.fromLTRB(16, 12, 16, 12 + MediaQuery.paddingOf(context).bottom),
            decoration: const BoxDecoration(color: CodoColors.pureSurface, border: Border(top: BorderSide(color: CodoColors.quietBorder))),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Expanded(child: TextField(controller: controller, minLines: 1, maxLines: 5, decoration: const InputDecoration(hintText: 'Décrivez votre situation'))),
                const SizedBox(width: 8),
                IconButton.filled(tooltip: 'Envoyer', onPressed: _ask, icon: const Icon(Icons.arrow_upward_rounded)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _AnswerView extends StatelessWidget {
  const _AnswerView({required this.answer});

  final CodoAnswer answer;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _Block(title: 'Votre situation', body: answer.situation),
        _Block(title: 'Ce que prévoit le droit', body: answer.lawSummary),
        if (answer.nextSteps.isNotEmpty) _ListBlock(title: 'Ce que vous pouvez faire', values: answer.nextSteps),
        if (answer.documentsNeeded.isNotEmpty) _ListBlock(title: 'Documents susceptibles d’être nécessaires', values: answer.documentsNeeded),
        if (answer.whereToAct.isNotEmpty) _ListBlock(title: 'Où effectuer la démarche', values: answer.whereToAct),
        if (answer.deadlines.isNotEmpty) _ListBlock(title: 'Délais', values: answer.deadlines),
        if (answer.attentionPoints.isNotEmpty) _ListBlock(title: 'Points nécessitant une attention particulière', values: answer.attentionPoints),
        const SizedBox(height: 22),
        Text('Sources', style: Theme.of(context).textTheme.titleLarge),
        const SizedBox(height: 10),
        ...answer.citations.map((citation) => ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.verified_outlined, color: CodoColors.civicGreen),
              title: Text(citation.label ?? citation.documentId),
              subtitle: Text('Version ${citation.version}${citation.articleId == null ? '' : ' • ${citation.articleId}'}${citation.trustLevel == null ? '' : ' • Source ${citation.trustLevel}'}'),
            )),
      ],
    );
  }
}

class _Block extends StatelessWidget {
  const _Block({required this.title, required this.body});
  final String title;
  final String body;
  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.only(bottom: 22),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(title, style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 8),
          Text(body),
        ]),
      );
}

class _ListBlock extends StatelessWidget {
  const _ListBlock({required this.title, required this.values});
  final String title;
  final List<String> values;
  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.only(bottom: 22),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(title, style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 8),
          ...values.map((value) => Padding(padding: const EdgeInsets.only(bottom: 6), child: Text('• $value'))),
        ]),
      );
}

class _AiIntro extends StatelessWidget {
  const _AiIntro();
  @override
  Widget build(BuildContext context) => Container(
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(color: CodoColors.pureSurface, border: Border.all(color: CodoColors.quietBorder), borderRadius: BorderRadius.circular(24)),
        child: const Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('Une réponse CODO doit distinguer :', style: TextStyle(fontWeight: FontWeight.w700)),
          SizedBox(height: 12),
          Text('Votre situation'),
          Text('Ce que prévoit le droit'),
          Text('Textes applicables'),
          Text('Ce que vous pouvez faire'),
          Text('Documents susceptibles d’être nécessaires'),
          Text('Où effectuer la démarche'),
          Text('Délais lorsqu’ils sont vérifiés'),
          Text('Points d’attention'),
          Text('Sources'),
        ]),
      );
}

class _QuestionBubble extends StatelessWidget {
  const _QuestionBubble({required this.question});
  final String question;
  @override
  Widget build(BuildContext context) => Align(
        alignment: Alignment.centerRight,
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 360),
          child: Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(color: CodoColors.legalInk, borderRadius: BorderRadius.circular(18)),
            child: Text(question, style: const TextStyle(color: Colors.white)),
          ),
        ),
      );
}
